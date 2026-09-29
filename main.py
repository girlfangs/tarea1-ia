"""
demo.py
-------
Corre una simulación de ejemplo sobre map1_bottleneck.txt con cada uno
de los 4 algoritmos implementados, usando el MISMO algoritmo para
todos los agentes en cada corrida (así se comparan entre sí). Esto es
la base sobre la que se debe construir el benchmarking de 80-200
iteraciones por (mapa, algoritmo) que pide el enunciado.
"""

import random
from collections import defaultdict

from grid import Grid
from agent import Agent
from environment import Simulation
from algorithms.uninformed import bfs, uniform_cost_search
from algorithms.informed import a_star, greedy_best_first
from algorithms.genetic import genetic_tournament
from progress import print_progress_bar

ALGORITHMS = {
    "bfs":          bfs,
    "dijkstra":     uniform_cost_search,
    "a-star":       a_star,
    "greedy":       greedy_best_first,
    "genetic":      genetic_tournament
}

MAPS = [
    'maps/map1_bottleneck.txt',
    'maps/map2_corporate.txt',
]


def load_map(path: str):
    with open(path) as f:
        return [line.rstrip("\n") for line in f if line.strip()]


def spawn_agents(grid: Grid, n: int, algorithm_name: str, seed: int = 0):
    random.seed(seed)
    free_cells = [
        (r, c)
        for r in range(grid.rows)
        for c in range(grid.cols)
        if grid.is_walkable((r, c)) and (r, c) not in grid.exits
    ]
    starts = random.sample(free_cells, min(n, len(free_cells)))
    return [Agent(i, pos, algorithm_name) for i, pos in enumerate(starts)]


def run_once(map_path: str, algo_name: str, n_agents: int = 15, seed: int = 0):
    layout  = load_map(map_path)
    grid    = Grid(layout)
    agents  = spawn_agents(grid, n_agents, algo_name, seed=seed)

    sim = Simulation(
        grid                    = grid,
        agents                  = agents,
        search_fn               = ALGORITHMS[algo_name],
        fire_spread_interval    = 3,
        max_turns               = 300,
    )
    return sim.run()


if __name__ == "__main__":
    iterations = 80


    for map in MAPS:
        print(f"for map {map}")
        results = defaultdict(list)

        for name in ALGORITHMS:
            avg = 0

            print_progress_bar(0, iterations-1, f"{name}, {map}")
            for seed in range(iterations):
                result = run_once(map, name, n_agents=50, seed=seed)
                print_progress_bar(seed, iterations-1, f"{name}, {map}")
                #print(f"{name:20s} -> supervivencia: {result.survival_rate:.0%}  "
                #    f"turnos hasta despeje: {result.turns_to_clear}")
                #print(f"{result.survival_rate} {result.turns_to_clear}")
                results[name].append(result)
            print("")

        for algo_name, algo_results in results.items():
            avg_rate = 0
            avg_turns = 0
            for result in algo_results:
                avg_rate += result.survival_rate
                avg_turns += result.turns_to_clear

            avg_rate /= len(algo_results)
            avg_turns /= len(algo_results)

            print(f"{algo_name}: -> supervivencia: {avg_rate:.3%}, turnos {avg_turns}")
