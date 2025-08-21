# evolutionary_loop.py
import random
from environment import Environment
from organism import Organism

class EvolutionaryLoop:
    """
    Drives the entire simulation by running generations and evolving the population.
    """
    def __init__(self, environment: Environment, generations: int, cycles_per_generation: int):
        self.environment = environment
        self.generations = generations
        self.cycles_per_generation = cycles_per_generation

    def run_simulation(self):
        """Runs the complete simulation from start to finish."""
        print("Starting the multi-objective homeostasis experiment...")
        self.environment.initialize_population()

        for gen in range(self.generations):
            print(f"\n--- Generation {gen+1}/{self.generations} ---")
            
            # 1. Run the life simulation for the current generation
            self.run_generation_cycle()
            
            # 2. Log the results of the generation that just lived
            self.environment.log_generation_data(gen + 1)

            # 3. Evolve the population to create the next generation
            self.evolve_population()
        
        print("\nSimulation complete.")

    def run_generation_cycle(self):
        """Simulates one lifetime for the current population."""
        for _ in range(self.cycles_per_generation):
            for organism in self.environment.organisms:
                if organism.is_alive:
                    organism.process_cycle()
                    
                    # Organisms have a chance to interact with the Oracle each cycle
                    if random.random() < 0.25:
                        problem_type, p_data, r_type, correct_ans = self.environment.oracle.present_problem()
                        
                        # The organism uses its genome to generate a solution
                        proposed_solution = organism.solve_problem(p_data)
                        
                        # Check if the solution is correct (with tolerance for floats)
                        is_correct = False
                        if problem_type in ["math_problem", "logic_problem"]:
                             if abs(proposed_solution - correct_ans) < 0.1:
                                is_correct = True
                        
                        if is_correct:
                            amount = self.environment.oracle.get_reward_amount(r_type)
                            organism.gain_resource(r_type, amount)
                        else:
                            # This method now exists in the Organism class
                            organism.trigger_error()
    
    def evolve_population(self):
        """Selects the fittest organisms and creates the next generation."""
        
        # --- KEY CHANGE: BREED FROM THE BEST, EVEN IF DEAD ---
        
        # First, check for any survivors
        survivors = [org for org in self.environment.organisms if org.is_alive]
        
        parents = []
        if survivors:
            # If we have survivors, they are the parents
            survivors.sort(key=lambda org: org.age, reverse=True)
            num_parents = max(2, int(self.environment.population_size * 0.2))
            parents = survivors[:num_parents]
        else:
            # EXTINCTION EVENT: No survivors. Breed from the longest-lived dead organisms.
            print("Extinction event! Breeding from the longest-lived organisms.")
            all_organisms = sorted(self.environment.organisms, key=lambda org: org.age, reverse=True)
            num_parents = max(2, int(self.environment.population_size * 0.2))
            parents = all_organisms[:num_parents]

        if not parents:
            # This should only happen if the simulation starts with 0 organisms.
            print("Complete failure. Resetting population.")
            self.environment.initialize_population()
            return

        next_generation = []
        
        # Elitism: Protect the very best parents by adding them directly
        elites_to_keep = int(len(parents) * 0.5) # Keep top 50% of parents
        for i in range(elites_to_keep):
            elite_organism = Organism(self.environment.genome_size)
            elite_organism.genome = parents[i].genome # Pass genome untouched
            next_generation.append(elite_organism)

        # Generate the rest of the population through crossover and mutation
        while len(next_generation) < self.environment.population_size:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            
            child_genome = self.environment.crossover_and_mutate(parent1.genome, parent2.genome)
            child_organism = Organism(self.environment.genome_size)
            child_organism.genome = child_genome
            next_generation.append(child_organism)
            
        self.environment.organisms = next_generation