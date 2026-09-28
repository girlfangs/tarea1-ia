"""
fire.py
-------
Maneja la propagación irreversible del incendio. Cada `spread_interval`
turnos, el fuego avanza a las celdas ortogonalmente adyacentes que no
sean muros. Una vez que una celda se quema, queda intransitable para
siempre (no hay reversión).
"""

from __future__ import annotations
from typing import List, Set, Tuple
from grid import Grid, CellType

Coord = Tuple[int, int]


class FireSpreader:
    def __init__(self, grid: Grid, origins: List[Coord], spread_interval: int = 3):
        self.grid                       = grid
        self.spread_interval            = spread_interval
        self.active_fire: Set[Coord]    = set()
        self.turn_counter               = 0

        for o in origins:
            self.grid.set_fire(o)
            self.active_fire.add(o)

    def tick(self) -> Set[Coord]:
        """Avanza un turno. Devuelve el conjunto de celdas recién quemadas
        (vacío si no correspondía propagar en este turno)."""
        self.turn_counter += 1
        newly_burned: Set[Coord] = set()

        if self.turn_counter % self.spread_interval != 0:
            return newly_burned

        frontier = list(self.active_fire)
        for pos in frontier:
            for nb in self._raw_neighbors(pos):
                if self._is_burnable(nb):
                    self.grid.set_fire(nb)
                    newly_burned.add(nb)

        self.active_fire |= newly_burned
        return newly_burned

    def _raw_neighbors(self, pos: Coord) -> List[Coord]:
        r, c = pos
        return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]

    def _is_burnable(self, pos: Coord) -> bool:
        if not self.grid.in_bounds(pos):
            return False
        cell = self.grid.cells[pos[0]][pos[1]]
        return cell not in (CellType.WALL, CellType.FIRE)

    def reached(self, pos: Coord) -> bool:
        """True si el fuego ya alcanzó esa celda (agente = baja)."""
        return pos in self.active_fire
