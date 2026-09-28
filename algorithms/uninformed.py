"""
uninformed.py
-------------
Dos algoritmos de búsqueda NO informada:

1. BFS: encuentra el camino con menos PASOS, ignorando por completo
   el costo de congestión. Sirve como línea base "ingenua".

2. Uniform Cost Search (Dijkstra): sí incorpora el costo dinámico de
   congestión de cada celda (grid.step_cost). Es la búsqueda no
   informada "correcta" quí porque el grafo tiene pesos variables.

Ambos devuelven None si no existe camino (por ejemplo, el fuego dejó
al agente aislado).
"""

from __future__ import annotations
from collections import deque
import heapq
from typing import List, Optional, Tuple, Dict

from grid import Grid

Coord = Tuple[int, int]


def bfs(grid: Grid, start: Coord, goals: List[Coord]) -> Optional[List[Coord]]:
    if start in goals:
        return []
    visited = {start}
    queue = deque([(start, [])])

    while queue:
        pos, path = queue.popleft()
        for nb in grid.neighbors(pos):
            if nb in visited:
                continue
            new_path = path + [nb]
            if nb in goals:
                return new_path
            visited.add(nb)
            queue.append((nb, new_path))
    return None


def uniform_cost_search(grid: Grid, start: Coord, goals: List[Coord]) -> Optional[List[Coord]]:
    counter = 0  # desempate estable en el heap
    frontier = [(0.0, counter, start, [])]
    best_cost: Dict[Coord, float] = {start: 0.0}

    while frontier:
        cost, _, pos, path = heapq.heappop(frontier)
        if pos in goals:
            return path
        if cost > best_cost.get(pos, float("inf")):
            continue
        for nb in grid.neighbors(pos):
            new_cost = cost + grid.step_cost(nb)
            if new_cost < best_cost.get(nb, float("inf")):
                best_cost[nb] = new_cost
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, nb, path + [nb]))
    return None
