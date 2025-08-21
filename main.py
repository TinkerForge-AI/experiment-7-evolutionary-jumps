# main.py
import matplotlib.pyplot as plt
from environment import Environment
from evolutionary_loop import EvolutionaryLoop

def plot_history(history):
    """Generates a plot of the simulation's history."""
    generations = [data['generation'] for data in history]
    avg_ages = [data['average_age'] for data in history]
    survivor_counts = [data['survivor_count'] for data in history]
    avg_discrepancies = [data['average_discrepancy'] for data in history]
    # cohesion_mean may be None for some generations; map to NaN so matplotlib skips them
    cohesion_means = [data.get('cohesion_mean') if data.get('cohesion_mean') is not None else float('nan') for data in history]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    fig.suptitle('Evolutionary Homeostasis Simulation Results')

    # Plot 1: Average Age and Survivor Count
    ax1.plot(generations, avg_ages, 'b-', label='Average Age (cycles)')
    ax1.set_ylabel('Average Age', color='b')
    ax1.tick_params('y', colors='b')
    ax1.grid(True)

    ax1b = ax1.twinx()
    ax1b.plot(generations, survivor_counts, 'r-', label='Survivor Count')
    ax1b.set_ylabel('Survivors', color='r')
    ax1b.tick_params('y', colors='r')

    # Plot 2: Average Discrepancy (Instability)
    ax2.plot(generations, avg_discrepancies, 'g-', label='Avg Discrepancy')
    ax2.set_ylabel('Average Discrepancy', color='g')
    ax2.tick_params('y', colors='g')
    ax2.grid(True)

    # Plot 3: Cohesion (monitor-derived metric)
    ax3.plot(generations, cohesion_means, 'm-', label='Cohesion (mean)')
    ax3.set_xlabel('Generation')
    ax3.set_ylabel('Cohesion (0-1)', color='m')
    ax3.tick_params('y', colors='m')
    ax3.grid(True)

    # Global legend
    fig.legend(loc='upper right')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('simulation_results.png')
    print("\nPlot of simulation results saved to 'simulation_results.png'")


if __name__ == "__main__":
    # --- Experiment Parameters ---
    POPULATION_SIZE = 100
    GENOME_SIZE = 2  # Each problem has two inputs, so two genes for weights.
    TOTAL_GENERATIONS = 2000
    CYCLES_PER_GENERATION = 150 # Increased lifespan to allow for more interactions

    # 1. Instantiate the environment with our parameters
    my_env = Environment(POPULATION_SIZE, GENOME_SIZE)
    
    # 2. Instantiate the evolutionary loop with the environment
    loop = EvolutionaryLoop(my_env, TOTAL_GENERATIONS, CYCLES_PER_GENERATION)
    
    # 3. Run the simulation
    loop.run_simulation()
    
    # 4. Plot the results for analysis
    plot_history(my_env.history["generation_data"])