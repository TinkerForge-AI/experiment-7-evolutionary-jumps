# environment.py
import random
from typing import List
from organism import Organism
from oracle import HumanInterfaceOracle
from monitor import Monitor

class Environment:
    """
    Manages the ecosystem: the population, the Oracle, and historical data.
    """
    def __init__(self, population_size: int, genome_size: int):
        self.population_size = population_size
        self.genome_size = genome_size
        self.organisms: List[Organism] = []
        self.oracle = HumanInterfaceOracle()
        self.monitor = Monitor()  # cohesion & stats
        self.history = {"generation_data": []}

    def initialize_population(self):
        """Creates the initial, randomly generated population of organisms."""
        self.organisms = [Organism(self.genome_size) for _ in range(self.population_size)]

    def log_generation_data(self, gen: int):
        """Logs key metrics for the generation that just completed its lifecycle."""
        living_organisms = [org for org in self.organisms if org.is_alive]
        dead_organisms = [org for org in self.organisms if not org.is_alive]
        
        all_organisms = living_organisms + dead_organisms

        if not all_organisms:
            return

        avg_age = sum(org.age for org in all_organisms) / len(all_organisms)
        avg_discrepancy = sum(org.cumulative_discrepancy for org in all_organisms) / len(all_organisms)
        survivor_count = len(living_organisms)

        # Monitor-derived metrics (cohesion & accuracy)
        mon = self.monitor.generation_metrics()
        cohesion_mean = mon.get("cohesion_mean")
        cohesion_median = mon.get("cohesion_median")
        accuracy = mon.get("accuracy")
        n_interactions = mon.get("n_interactions")

        leap = self.monitor.check_generation_leap(gen, cohesion_mean, accuracy)
        if leap:
            print(
                f"✨ Evolutionary leap @ Gen {leap['generation']}: "
                f"cohesion={leap['cohesion']:.3f}, acc={leap['accuracy'] if leap['accuracy'] is not None else 'n/a'} "
                f"(baseline μ={leap['baseline_mean']:.3f}, σ={leap['baseline_std']:.3f}; {leap['reason']})"
            )
        
        self.monitor.log_generation_row({
            "generation": gen,
            "average_age": avg_age,
            "average_discrepancy": avg_discrepancy,
            "survivor_count": survivor_count,
            "cohesion_mean": cohesion_mean,
            "cohesion_median": cohesion_median,
            "oracle_accuracy": accuracy,
            "oracle_interactions": n_interactions,
            "leap_flag": 1 if leap else 0,
            "z_score": (leap["z_score"] if leap else None),
        })

        # Store data for plotting
        self.history["generation_data"].append({
            "generation": gen,
            "average_age": avg_age,
            "average_discrepancy": avg_discrepancy,
            "survivor_count": survivor_count,
            "cohesion_mean": cohesion_mean,
            "cohesion_median": cohesion_median,
            "oracle_accuracy": accuracy,
            "oracle_interactions": n_interactions,
        })
        
        # Concise summary print
        coh_str = f"{cohesion_mean:.3f}" if cohesion_mean is not None else "n/a"
        acc_str = f"{accuracy:.2%}" if accuracy is not None else "n/a"
        print(
            f"Avg Age: {avg_age:.2f} | Avg Discrepancy: {avg_discrepancy:.2f} | "
            f"Survivors: {survivor_count}/{self.population_size} | "
            f"Cohesion(mean): {coh_str} | Acc: {acc_str} | n={n_interactions}"
        )
        if living_organisms:
            fittest_survivor = max(living_organisms, key=lambda org: org.age)
            print(f"Fittest Survivor: Age={fittest_survivor.age}, Genome={fittest_survivor.genome}")

    def crossover_and_mutate(self, genome1: List[float], genome2: List[float]) -> List[float]:
        """Performs crossover and mutation to create a new genome."""
        # Single-point crossover
        if self.genome_size > 1:
            crossover_point = random.randint(1, self.genome_size - 1)
            new_genome = genome1[:crossover_point] + genome2[crossover_point:]
        else:
            # If genome is too small for crossover, just copy one parent's genome
            new_genome = list(genome1)
        
        # Apply mutation
        mutation_rate = 0.1
        for i in range(len(new_genome)):
            if random.random() < mutation_rate:
                new_genome[i] += random.gauss(0, 0.5) # Add small Gaussian noise
        
        return new_genome