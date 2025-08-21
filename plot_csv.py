import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt

def read_csv_rows(path):
    rows = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def to_float(x, default=None):
    if x is None or x == "":
        return default
    try:
        return float(x)
    except ValueError:
        return default

def main():
    ap = argparse.ArgumentParser(description="Plot evolution_summary.csv with leap markers.")
    ap.add_argument("--csv", default="evolution_summary.csv", help="Path to CSV (default: evolution_summary.csv)")
    ap.add_argument("--out1", default="evolution_summary_plot.png", help="Output PNG for cohesion/accuracy (default: evolution_summary_plot.png)")
    ap.add_argument("--out2", default="evolution_system_plot.png", help="Output PNG for survivors/discrepancy (default: evolution_system_plot.png)")
    ap.add_argument("--annotate-z", action="store_true", help="Annotate leap markers with z-scores")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    rows = read_csv_rows(csv_path)
    if not rows:
        raise SystemExit("CSV has no data rows. Run the simulation first.")

    gens = []
    avg_age = []
    avg_disc = []
    surv = []
    coh_mean = []
    coh_median = []
    acc = []
    n_int = []
    leap = []
    z_scores = []

    for r in rows:
        gens.append(int(r.get("generation", 0)))
        avg_age.append(to_float(r.get("average_age")))
        avg_disc.append(to_float(r.get("average_discrepancy")))
        surv.append(to_float(r.get("survivor_count")))
        coh_mean.append(to_float(r.get("cohesion_mean")))
        coh_median.append(to_float(r.get("cohesion_median")))
        acc.append(to_float(r.get("oracle_accuracy")))
        n_int.append(to_float(r.get("oracle_interactions")))
        leap_flag = r.get("leap_flag", 0)
        leap.append(int(float(leap_flag)) if leap_flag not in (None, "") else 0)
        z_scores.append(to_float(r.get("z_score")))

    # -------------------------
    # Figure 1: Cohesion + Accuracy + leap markers (+ optional z-labels)
    # -------------------------
    fig1 = plt.figure(figsize=(12, 6))
    ax1 = fig1.gca()
    ax1.plot(gens, coh_mean, label="Cohesion (mean)")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Cohesion (0–1)")
    ax1.grid(True)

    ax1b = ax1.twinx()
    ax1b.plot(gens, acc, linestyle="--", label="Accuracy")
    ax1b.set_ylabel("Accuracy (0–1)")

    # Leap markers
    leap_gens = [g for g, f in zip(gens, leap) if f == 1]
    leap_vals = [c for c, f in zip(coh_mean, leap) if f == 1]
    leap_zs   = [z for z, f in zip(z_scores, leap) if f == 1]
    if leap_gens:
        ax1.scatter(leap_gens, leap_vals, marker="o", s=40, label="Leaps")
        if args.annotate_z:
            for x, y, z in zip(leap_gens, leap_vals, leap_zs):
                if z is not None:
                    ax1.annotate(f"z={z:.2f}", (x, y), textcoords="offset points", xytext=(6, 6))

    # Combined legend
    lines, labels = [], []
    for a in (ax1, ax1b):
        lns, lbs = a.get_legend_handles_labels()
        lines.extend(lns); labels.extend(lbs)
    if labels:
        ax1.legend(lines, labels, loc="best")

    fig1.tight_layout()
    fig1.savefig(args.out1)
    print(f"Saved plot -> {args.out1}")

    # -------------------------
    # Figure 2: Survivors + Discrepancy
    # -------------------------
    fig2 = plt.figure(figsize=(12, 6))
    ax2 = fig2.gca()
    ax2.plot(gens, surv, label="Survivor Count")
    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Survivors")
    ax2.grid(True)

    ax2b = ax2.twinx()
    ax2b.plot(gens, avg_disc, linestyle="--", label="Average Discrepancy")
    ax2b.set_ylabel("Avg Discrepancy")

    # Combined legend
    lines2, labels2 = [], []
    for a in (ax2, ax2b):
        lns, lbs = a.get_legend_handles_labels()
        lines2.extend(lns); labels2.extend(lbs)
    if labels2:
        ax2.legend(lines2, labels2, loc="best")

    fig2.tight_layout()
    fig2.savefig(args.out2)
    print(f"Saved plot -> {args.out2}")

if __name__ == "__main__":
    main()

    # python plot_csv.py --csv evolution_summary.csv --out evolution_summary_plot.png
    # python plot_csv.py --annotate-z
