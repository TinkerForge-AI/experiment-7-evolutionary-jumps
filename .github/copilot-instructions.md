## Quick context

This repo implements a small evolutionary simulation: digital organisms with simple genomes try to solve problems presented by an `Oracle` to maintain homeostatic variables. Key scripts: `main.py` (experiment runner), `environment.py` (population/oracle/history), `evolutionary_loop.py` (generation lifecycle & evolution), `organism.py` (individual behavior), and `oracle.py` (problems & rewards).

## Big-picture architecture

- Environment owns the population, the `HumanInterfaceOracle`, and `history` (see `Environment.history["generation_data"]`).
- `EvolutionaryLoop.run_simulation()` runs N generations; each generation runs `cycles_per_generation` cycles where each organism `process_cycle()` and occasionally interacts with the `Oracle`.
- Evolution happens in `EvolutionaryLoop.evolve_population()` with these notable rules:
  - If there are survivors: select top organisms by age (top ~20%) as parents.
  - If extinct: breed from longest-lived dead organisms (explicit extinction-handling).
  - Elitism: top 50% of parents are cloned unchanged into next generation.
  - Children are created with `Environment.crossover_and_mutate()` (single-point crossover; mutation_rate=0.1; Gaussian perturbation).

## Important, project-specific patterns and rules

- Genome semantics: `Organism.solve_problem(problem_data)` uses a linear model: sum(input_i * gene_i). Example: to solve `math_problem` (a+b) the target genome approximates `[1.0, 1.0]` (see `oracle.py`).
- Homeostatic model: organism variables (e.g., `compute_load`, `signal_integrity`) have `current`, `target_range`, and `decay_rate`. Rewards apply via `gain_resource()` and are clamped to target ranges.
- Death is driven by `cumulative_discrepancy` thresholds; there are multiple thresholds in `process_cycle()` (note they were tuned in this branch). Search for numeric thresholds in `organism.py` if altering survivability.
- Oracle mapping: problems -> resource types are in `HumanInterfaceOracle.resource_map`. Rewards amounts are configured in `HumanInterfaceOracle.reward_amounts`.

## How to run, debug, and inspect results

- Run the experiment locally:

  python3 main.py

  Output: console logs per generation and `simulation_results.png` saved by `main.plot_history()`.

- Quick debug points:
  - To see population metrics during runtime inspect `Environment.log_generation_data()` (prints fittest survivor and averages).
  - To change experiment scale, edit constants in `main.py`: `POPULATION_SIZE`, `GENOME_SIZE`, `TOTAL_GENERATIONS`, `CYCLES_PER_GENERATION`.
  - To reproduce behavior deterministically, add `random.seed(...)` at the top of `main.py` and also seed numpy if used.

## Files that exemplify important patterns

- `organism.py` — linear solve model, discrepancy calculation, death thresholds, reward handling.
- `oracle.py` — problem generation, `resource_map`, and `reward_amounts` (tuning here changes selective pressure).
- `evolutionary_loop.py` — lifecycle, extinction handling, elitism, and how children are generated from parent genomes.
- `environment.py` — population initialization, crossover/mutation implementation, and where historical metrics are stored.

## Integration & dependencies

- External deps declared in `requirements.txt`: `matplotlib`, `numpy` (numpy is present but not used heavily here). Use `pip install -r requirements.txt`.
- There are no external network calls; changes are local state only.

## Typical code edit targets for agents

- Modify selection pressure: change parent-selection percentage and elitism in `evolutionary_loop.py`.
- Change reward shaping: edit `HumanInterfaceOracle.reward_amounts` to bias evolution toward different homeostatic variables.
- Extend problems: add new problem types in `oracle.py` and adapt `Organism.solve_problem` to handle different input encodings.

## Small examples to reference

- Problem generation (oracle): for `math_problem`, `problem_data=(a,b)` and `correct_answer=a+b` — evolve genes close to `[1,1]`.
- Crossover: `Environment.crossover_and_mutate()` performs a single-point crossover and then mutates each gene with probability 0.1.

## Do not change without inspection

- Numeric thresholds in `organism.py` (death/discrepancy) and reward amounts in `oracle.py` — these interact nonlinearly with population dynamics.

---
If anything here is unclear or you want the file to include additional examples (tests, debugging snippets, or a developer checklist), tell me which area to expand.
