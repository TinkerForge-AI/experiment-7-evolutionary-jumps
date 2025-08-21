from collections import deque
from statistics import mean, median, pstdev
import json, os, csv
from pathlib import Path

class Monitor:
    """
    Tracks per-interaction stats and computes a simple 'cohesion score'
    between the Oracle's correct answers and the organism's proposals.
    """
    def __init__(self):
        self.reset_generation()
        self.leap = EvolutionaryLeapDetector()
        self.csv = EvolutionCSVLogger()
        self.log_path = os.path.join(os.path.dirname(__file__), "evolutionary_leaps.log")
    
    def reset_generation(self):
        self._interactions = []
    
    def _scale_for(self, problem_type: str) -> float:
        # Heuristic normalization factors based on ranges in oracle.py
        return 20.0 if problem_type in ("math_problem", "logic_problem") else 1.0
    
    def record_interaction(self, *, problem_type: str, resource_type: str,
                           correct_answer: float, proposed_solution: float, is_correct: bool):
        scale = self._scale_for(problem_type)
        abs_error = abs(proposed_solution - correct_answer)
        cohesion = max(0.0, 1.0 - (abs_error / scale))
        self._interactions.append({
            "problem_type": problem_type,
            "resource_type": resource_type,
            "correct": is_correct,
            "abs_error": abs_error,
            "cohesion": cohesion,
        })
    
    def generation_metrics(self):
        if not self._interactions:
            return {
                "n_interactions": 0,
                "accuracy": 0.0,
                "mean_abs_error": None,
                "cohesion_mean": None,
                "cohesion_median": None,
            }
        acc = mean(1.0 if it["correct"] else 0.0 for it in self._interactions)
        mae = mean(it["abs_error"] for it in self._interactions)
        coh_vals = [it["cohesion"] for it in self._interactions]
        return {
            "n_interactions": len(self._interactions),
            "accuracy": acc,
            "mean_abs_error": mae,
            "cohesion_mean": mean(coh_vals),
            "cohesion_median": median(coh_vals),
        }
    
    def check_generation_leap(self, gen: int, cohesion_mean, accuracy):
        return self.leap.update_and_check(gen, cohesion_mean, accuracy)
    
    def log_generation_row(self, row: dict):
        self.csv.append(row)

class EvolutionCSVLogger:
    def __init__(self, path: str | None = None):
        self.path = path or os.path.join(os.path.dirname(__file__), "evolution_summary.csv")
        self.headers = [
            "generation",
            "average_age",
            "average_discrepancy",
            "survivor_count",
            "cohesion_mean",
            "cohesion_median",
            "oracle_accuracy",
            "oracle_interactions",
            "leap_flag",
            "z_score",
        ]
        self._ensure_header()

    def _ensure_header(self):
        if not os.path.exists(self.path) or os.path.getsize(self.path) == 0:
            with open(self.path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

    def append(self, row: dict):
        # Coerce None → "" for CSV friendliness
        row = {k: ("" if v is None else v) for k, v in row.items()}
        # Ensure header exists then append
        self._ensure_header()
        with open(self.path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(row)

class EvolutionaryLeapDetector:
    """
    Tracks recent generation-level metrics and flags 'leaps' when current
    cohesion meaningfully exceeds the rolling baseline.
    """
    def __init__(self, window=20, z_min=2.0, delta_min=0.08, acc_floor=0.0):
        self.window = window
        self.z_min = z_min
        self.delta_min = delta_min
        self.acc_floor = acc_floor
        self._coh_ring = deque(maxlen=window)
        self._best_coh = None

    def update_and_check(self, gen: int, cohesion_mean, accuracy) -> dict | None:
        """
        Returns a dict describing the leap if detected, else None.
        """
        # If we don't have a current cohesion, or no history yet, just record.
        if cohesion_mean is None:
            self._append(cohesion_mean)
            return None

        recent = list(self._coh_ring)
        self._append(cohesion_mean)

        # Not enough history yet -> cannot form a baseline
        if len(recent) < max(5, int(0.5 * self.window)):
            self._best_coh = cohesion_mean if self._best_coh is None else max(self._best_coh, cohesion_mean)
            return None

        mu = mean(recent)
        sigma = pstdev(recent)  # population stdev; small windows are fine here
        eps = 1e-6
        z = (cohesion_mean - mu) / (sigma + eps)

        # Check against best-so-far margin too
        improved_vs_best = (self._best_coh is None) or (cohesion_mean >= self._best_coh + self.delta_min)
        z_pass = z >= self.z_min
        acc_pass = (accuracy is None) or (accuracy >= self.acc_floor)

        is_leap = acc_pass and (z_pass or improved_vs_best)

        # update best
        if (self._best_coh is None) or (cohesion_mean > self._best_coh):
            self._best_coh = cohesion_mean

        if not is_leap:
            return None

        reason_bits = []
        if z_pass: reason_bits.append(f"z={z:.2f} (≥ {self.z_min})")
        if improved_vs_best: reason_bits.append(f"best+Δ ({cohesion_mean:.3f} vs {mu:.3f}/{self._best_coh:.3f} best)")
        if not acc_pass: reason_bits.append("low-accuracy (ignored)")

        leap_info = {
            "generation": gen,
            "type": "evolutionary_leap",
            "cohesion": cohesion_mean,
            "accuracy": accuracy,
            "baseline_mean": mu,
            "baseline_std": sigma,
            "z_score": z,
            "reason": "; ".join(reason_bits)
        }

        # --- Append to log file ---
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(leap_info) + "\n")
        except Exception as e:
            print(f"[Monitor] Failed to log leap: {e}")

        return leap_info

    def _append(self, v):
        if v is not None:
            self._coh_ring.append(v)
