"""
genetic.py
----------
Algoritmo genético con selección por TORNEO, como función de búsqueda
compatible con el resto (grid, start, goals) -> Optional[List[Coord]].

Representación:
  Cromosoma = lista de movimientos (0=arriba, 1=abajo, 2=izq, 3=der).
  Se "decodifica" caminando sobre la grilla desde `start`:
    - un movimiento a celda no transitable (muro/fuego/fuera) se pierde
      (equivale a esperar, y cuesta 1);
    - si el agente vuelve a una celda ya visitada, se elimina el ciclo;
    - al llegar a una salida se detiene.

Fitness (se MINIMIZA):
  - Si llega a la salida: suma de grid.step_cost de las celdas pisadas
    (incluye congestión, igual que Dijkstra/A*).
  - Si no llega: PENALTY + 10 * distancia Manhattan final + costo.

Operadores:
  - Selección: torneo de tamaño k (se elige al azar k individuos y gana
    el de menor fitness).
  - Cruce: un punto.
  - Mutación: por gen, con probabilidad `mutation_rate`.
  - Elitismo: los `elite` mejores pasan intactos.

Devuelve None si ningún individuo alcanza la salida (igual que los demás).
Es estocástico: no garantiza el camino óptimo.
"""

from __future__ import annotations
import random
from typing import List, Optional, Tuple

from grid import Grid

Coord = Tuple[int, int]

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
PENALTY = 1000.0


def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _decode(grid: Grid, start: Coord, genes: List[int], goals: List[Coord]):
    """Camina el cromosoma. Devuelve (camino, llegó, costo, pos_final)."""
    pos = start
    trail = [start]
    index = {start: 0}
    cost = 0.0
    reached = False

    for g in genes:
        dr, dc = MOVES[g]
        nxt = (pos[0] + dr, pos[1] + dc)
        if not grid.is_walkable(nxt):
            cost += 1.0  # movimiento desperdiciado
            continue

        pos = nxt
        cost += grid.step_cost(pos)

        if pos in index:  # ciclo: recortar
            idx = index[pos]
            for removed in trail[idx + 1:]:
                del index[removed]
            trail = trail[: idx + 1]
        else:
            index[pos] = len(trail)
            trail.append(pos)

        if pos in goals:
            reached = True
            break

    return trail[1:], reached, cost, pos


def _fitness(grid: Grid, start: Coord, genes: List[int], goals: List[Coord]):
    path, reached, cost, pos = _decode(grid, start, genes, goals)
    if reached:
        return cost, path, True
    return PENALTY + 10 * grid.nearest_exit_heuristic(pos) + cost, path, False


def _random_individual(length: int, start: Coord, target: Coord,
                       rng: random.Random, bias: float) -> List[int]:
    """Con probabilidad `bias`, el gen apunta hacia la salida objetivo."""
    dr = (target[0] > start[0]) - (target[0] < start[0])
    dc = (target[1] > start[1]) - (target[1] < start[1])
    good = []
    if dr < 0: good.append(0)
    if dr > 0: good.append(1)
    if dc < 0: good.append(2)
    if dc > 0: good.append(3)

    return [
        rng.choice(good) if good and rng.random() < bias else rng.randrange(4)
        for _ in range(length)
    ]


def _tournament(scored, k: int, rng: random.Random) -> List[int]:
    contenders = rng.sample(scored, min(k, len(scored)))
    return min(contenders, key=lambda s: s[0])[1]


def genetic_tournament(
    grid: Grid,
    start: Coord,
    goals: List[Coord],
    pop_size: int = 40,
    generations: int = 40,
    tournament_k: int = 3,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.05,
    elite: int = 2,
    rng: Optional[random.Random] = None,
) -> Optional[List[Coord]]:
    if start in goals:
        return []

    # RNG local: no toca el random global que usa spawn_agents.
    # Determinista por posición inicial => corridas reproducibles.
    rng = rng or random.Random(start[0] * 10007 + start[1])

    target = min(goals, key=lambda g: _manhattan(start, g))
    length = 2 * _manhattan(start, target) + 10

    # Mitad de la población sesgada hacia la salida, mitad aleatoria pura.
    population = [
        _random_individual(length, start, target, rng, bias=0.6 if i % 2 else 0.0)
        for i in range(pop_size)
    ]

    best_cost, best_path, best_ok = float("inf"), None, False

    for _ in range(generations):
        scored = []
        for genes in population:
            fit, path, ok = _fitness(grid, start, genes, goals)
            scored.append((fit, genes))
            if ok and fit < best_cost:
                best_cost, best_path, best_ok = fit, path, True

        scored.sort(key=lambda s: s[0])
        next_pop = [list(g) for _, g in scored[:elite]]  # elitismo

        while len(next_pop) < pop_size:
            p1 = _tournament(scored, tournament_k, rng)
            p2 = _tournament(scored, tournament_k, rng)

            if rng.random() < crossover_rate and length > 1:
                cut = rng.randrange(1, length)
                child = p1[:cut] + p2[cut:]
            else:
                child = list(p1)

            for i in range(length):
                if rng.random() < mutation_rate:
                    child[i] = rng.randrange(4)
            next_pop.append(child)

        population = next_pop

    return best_path if best_ok else None
