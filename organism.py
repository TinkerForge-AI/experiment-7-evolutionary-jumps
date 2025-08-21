# organism.py
import random

class Organism:
    """
    A digital organism driven by a multi-objective homeostatic model.
    Its goal is to maintain key internal variables within a target range to survive.
    """
    def __init__(self, genome_size: int):
        # Homeostatic variables with their target ranges and natural decay rates
        self.homeostatic_variables = {
            # SLOWED DOWN DECAY
            "compute_load": {"current": 50, "target_range": [30, 95], "decay_rate": -0.34}, # Was -0.8
            "signal_integrity": {"current": 90, "target_range": [70, 100], "decay_rate": -0.14}, # Was -0.4
        }
        
        # The genome now directly influences behavior.
        self.genome = [random.uniform(-1, 1) for _ in range(genome_size)]
        
        self.is_alive = True
        self.cumulative_discrepancy = 0
        self.age = 0

    def calculate_discrepancy(self) -> float:
        """Calculates the total "pain" from being outside target ranges."""
        total_discrepancy = 0
        for var in self.homeostatic_variables.values():
            current = var["current"]
            min_target, max_target = var["target_range"]
            if current < min_target:
                total_discrepancy += (min_target - current)**2
            elif current > max_target:
                total_discrepancy += (current - max_target)**2
        return total_discrepancy

    def process_cycle(self):
        """Simulates one clock cycle of life."""

        # INCREASED DEATH THRESHOLD
        if self.cumulative_discrepancy > 4500: # Was 2500
            self.is_alive = False

        if not self.is_alive:
            return

        self.age += 1

        
        # Apply natural decay to all variables
        for var in self.homeostatic_variables.values():
            var["current"] += var["decay_rate"]
        
        self.cumulative_discrepancy += self.calculate_discrepancy()

        # Death occurs if cumulative instability becomes too high
        if self.cumulative_discrepancy > 2500:
            self.is_alive = False

    def gain_resource(self, resource_type: str, amount: float):
        """
        Applies a contextual reward to a homeostatic variable.
        """
        if resource_type == "compute_load":
            # For compute load, the "reward" is a reduction in load.
            self.homeostatic_variables[resource_type]["current"] -= amount
            # Clamp the value so it doesn't go below it's ideal states
            if self.homeostatic_variables[resource_type]["current"] < self.homeostatic_variables[resource_type]["target_range"][0]:
                self.homeostatic_variables[resource_type]["current"] = self.homeostatic_variables[resource_type]["target_range"][0]

        elif resource_type == "signal_integrity":
            # For signal integrity, the reward is a restoration.
            self.homeostatic_variables[resource_type]["current"] += amount
            # Clamp the value so it doesn't exceed it's maximum 
            if self.homeostatic_variables[resource_type]["current"] > self.homeostatic_variables[resource_type]["target_range"][1]:
                self.homeostatic_variables[resource_type]["current"] = self.homeostatic_variables[resource_type]["target_range"][1]

    def trigger_error(self):
        """Penalizes the organism for an incorrect solution."""
        # A failed action increases instability
        self.cumulative_discrepancy += 50

    def solve_problem(self, problem_data: tuple) -> float:
        """
        **CRITICAL CHANGE**: Uses the genome to produce a solution.
        The genome acts as weights for the input data.
        """
        # Ensure there are enough genes for the problem data
        if len(problem_data) > len(self.genome):
            return 0 # Cannot solve

        # Simple linear model: solution = (input1 * gene1) + (input2 * gene2) + ...
        solution = 0
        for i, value in enumerate(problem_data):
            solution += value * self.genome[i]
        return solution