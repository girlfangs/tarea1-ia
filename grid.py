"""
grid.py
--------
Representa el entorno como una grilla 2D. Cada celda tiene un tipo
(vacía, muro, salida, fuego) y un contador de ocupación (cuántos
agentes están cruzando/parados en ella en el turno actual).

La función de costo de congestión es el corazón del enunciado: entre
más agentes usan una misma celda, más caro es atravesarla. Se deja
como una función intercambiable (lineal, cuadrática, exponencial).
"""

from __future__ import annotations
from enum import Enum
from typing import List, Tuple, Callable
import math


class CellType(Enum):
    EMPTY   = "."
    WALL    = "#"
    EXIT    = "E"
    FIRE    = "F"


Coord = Tuple[int, int]  # (fila, columna)


# ---------------------------------------------------------------------
# Funciones de costo por congestión (elige una o crea la tuya)
# ---------------------------------------------------------------------
def linear_congestion_cost(base_cost: float, occupancy: int, k: float = 1.0) -> float:
    return base_cost * (1 + k * occupancy)


def quadratic_congestion_cost(base_cost: float, occupancy: int, k: float = 0.5) -> float:
    return base_cost * (1 + k * occupancy ** 2)


def exponential_congestion_cost(base_cost: float, occupancy: int, k: float = 0.35) -> float:
    return base_cost * math.exp(k * occupancy)


class Grid:
    def __init__(self, layout: List[str], congestion_fn: Callable[[float, int], float] = None):
        """
        layout: lista de strings, cada char es un CellType.value
                ej: ["#####", "#..E#", "#####"]
        congestion_fn: función(base_cost, occupancy) -> costo final.
                       Por defecto usa costo cuadrático.
        """
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.cells: List[List[CellType]] = [
            [CellType(ch) for ch in row] for row in layout
        ]
        self.occupancy: List[List[int]] = [[0] * self.cols for _ in range(self.rows)]
        self.capacity_per_cell = 1  # celdas > capacidad generan sobrecosto fuerte
        self.congestion_fn = congestion_fn or (lambda base, occ: quadratic_congestion_cost(base, occ))

        self.exits: List[Coord] = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.cells[r][c] == CellType.EXIT
        ]

    # ------------------------------------------------------------------
    def in_bounds(self, pos: Coord) -> bool:
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, pos: Coord) -> bool:
        if not self.in_bounds(pos):
            return False
        return self.cells[pos[0]][pos[1]] not in (CellType.WALL, CellType.FIRE)

    def neighbors(self, pos: Coord) -> List[Coord]:
        """Movimientos ortogonales válidos (sin incluir 'esperar')."""
        r, c = pos
        candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [p for p in candidates if self.is_walkable(p)]

    def step_cost(self, pos: Coord) -> float:
        """Costo de entrar/permanecer en `pos`, penalizado por congestión."""
        occ = self.occupancy[pos[0]][pos[1]]
        return self.congestion_fn(1.0, occ)

    # ------------------------------------------------------------------
    def set_fire(self, pos: Coord) -> None:
        if self.in_bounds(pos):
            self.cells[pos[0]][pos[1]] = CellType.FIRE

    def is_fire(self, pos: Coord) -> bool:
        return self.in_bounds(pos) and self.cells[pos[0]][pos[1]] == CellType.FIRE

    def get_all_fires(self) -> List[Coord]:
        fires: List[Coord] = []
        for r, row in enumerate(self.cells):
            for c, cell in enumerate(row):
                if cell == CellType.FIRE:
                    fires.append((r, c))
        return fires

    def nearest_exit_heuristic(self, pos: Coord) -> int:
        """Distancia Manhattan a la salida más cercana (heurística admisible:
        no sobreestima nunca, porque el costo mínimo real por paso es 1 y
        aquí no hay movimiento diagonal)."""
        r, c = pos
        return min(abs(r - er) + abs(c - ec) for er, ec in self.exits)

    def clear_occupancy(self) -> None:
        self.occupancy = [[0] * self.cols for _ in range(self.rows)]

    def add_occupancy(self, pos: Coord, amount: int = 1) -> None:
        r, c = pos
        self.occupancy[r][c] += amount
