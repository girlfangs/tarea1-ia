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
from grid import Grid
from agent import Agent
from environment import Simulation
from algorithms.uninformed import bfs, uniform_cost_search
from algorithms.informed import a_star, greedy_best_first

ALGORITHMS = {
    "BFS":                  bfs,
    "UCS (Dijkstra)":       uniform_cost_search,
    "A*":                   a_star,
    "Greedy Best-First":    greedy_best_first,
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
        fire_spread_interval    = 1,
        max_turns               = 300,
    )
    return sim.run()


if __name__ == "__main__":
    for map in MAPS:
        print(f"for map {map}")
        for name in ALGORITHMS:
            result = run_once(map, name, n_agents=15, seed=1)
            print(f"{name:20s} -> supervivencia: {result.survival_rate:.0%}  "
                f"turnos hasta despeje: {result.turns_to_clear}")
