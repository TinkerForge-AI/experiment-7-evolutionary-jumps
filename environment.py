# environment.py
import random
from typing import List
from organism import Organism
from oracle import HumanInterfaceOracle

class Environment:
    """
    Manages the ecosystem: the population, the Oracle, and historical data.
    """
    def __init__(self, population_size: int, genome_size: int):
        self.population_size = population_size
        self.genome_size = genome_size
        self.organisms: List[Organism] = []
        self.oracle = HumanInterfaceOracle()
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

        # Store data for plotting
        self.history["generation_data"].append({
            "generation": gen,
            "average_age": avg_age,
            "average_discrepancy": avg_discrepancy,
            "survivor_count": survivor_count,
        })
        
        # Print a concise summary for immediate feedback
        print(f"Avg Age: {avg_age:.2f} | Avg Discrepancy: {avg_discrepancy:.2f} | Survivors: {survivor_count}/{self.population_size}")
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