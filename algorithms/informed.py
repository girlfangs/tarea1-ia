"""
informed.py
-----------
Dos algoritmos de búsqueda INFORMADA, guiados por la heurística de
distancia Manhattan a la salida más cercana (grid.nearest_exit_heuristic).
Es admisible: nunca sobreestima el costo real restante, ya que el
movimiento es ortogonal y el costo mínimo por paso es 1.

1. A*: f(n) = g(n) + h(n). Óptimo y completo dado que h es admisible.
2. Greedy Best-First: f(n) = h(n) únicamente. Más rápido en la práctica
   pero no garantiza el camino óptimo; útil para comparar velocidad
   de cómputo vs. calidad de la ruta en el benchmarking.
"""

from __future__ import annotations
import heapq
from typing import List, Optional, Tuple, Dict

from grid import Grid

Coord = Tuple[int, int]


def _reconstruct(came_from: Dict[Coord, Coord], current: Coord, start: Coord) -> List[Coord]:
    path = [current]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path[1:]  # sin incluir la posición inicial


def a_star(grid: Grid, start: Coord, goals: List[Coord]) -> Optional[List[Coord]]:
    counter = 0
    open_set = [(grid.nearest_exit_heuristic(start), counter, start)]
    came_from: Dict[Coord, Coord] = {}
    g_score: Dict[Coord, float] = {start: 0.0}

    while open_set:
        _, _, current = heapq.heappop(open_set)
        if current in goals:
            return _reconstruct(came_from, current, start)

        for nb in grid.neighbors(current):
            tentative_g = g_score[current] + grid.step_cost(nb)
            if tentative_g < g_score.get(nb, float("inf")):
                came_from[nb] = current
                g_score[nb] = tentative_g
                f = tentative_g + grid.nearest_exit_heuristic(nb)
                counter += 1
                heapq.heappush(open_set, (f, counter, nb))
    return None


def greedy_best_first(grid: Grid, start: Coord, goals: List[Coord]) -> Optional[List[Coord]]:
    counter = 0
    open_set = [(grid.nearest_exit_heuristic(start), counter, start)]
    came_from: Dict[Coord, Coord] = {}
    visited = {start}

    while open_set:
        _, _, current = heapq.heappop(open_set)
        if current in goals:
            return _reconstruct(came_from, current, start)

        for nb in grid.neighbors(current):
            if nb not in visited:
                visited.add(nb)
                came_from[nb] = current
                counter += 1
                heapq.heappush(open_set, (grid.nearest_exit_heuristic(nb), counter, nb))
    return None
