# oracle.py
import random
from typing import Tuple

class HumanInterfaceOracle:
    """
    Simulates the external interface, providing problems and resources.
    """
    def __init__(self):
        self.resource_map = {
            "math_problem": "compute_load",
            "logic_problem": "signal_integrity",
        }
        # INCREASED REWARDS
        self.reward_amounts = {
            "compute_load": 35.0, # Was 25.0
            "signal_integrity": 30.0, # Was 20.0
        }

    def present_problem(self) -> Tuple[str, tuple, str, float]:
        """
        Generates a problem, the resource it provides, and the correct answer.
        """
        problem_type = random.choice(list(self.resource_map.keys()))
        resource_type = self.resource_map[problem_type]

        problem_data = tuple()
        correct_answer = 0.0

        if problem_type == "math_problem":
            # Problem: a + b. The organism must evolve a genome close to [1.0, 1.0]
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            problem_data = (num1, num2)
            correct_answer = float(num1 + num2)
            
        elif problem_type == "logic_problem":
            # Problem: a*2 - b. The organism must evolve a genome close to [2.0, -1.0]
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            problem_data = (num1, num2)
            correct_answer = float(num1 * 2 - num2)
            
        return problem_type, problem_data, resource_type, correct_answer

    def get_reward_amount(self, resource_type: str) -> float:
        """Returns the amount of reward for a given resource type."""
        return self.reward_amounts.get(resource_type, 0.0)