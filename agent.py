"""
agent.py
--------
Representa a cada persona del grupo liderado por Sebastián.
Un agente tiene una posición, un plan de ruta (lista de coordenadas)
calculado por alguno de los algoritmos de búsqueda, y un estado:
EVACUATING -> SAFE (llegó a la salida) o DEAD (alcanzado por el fuego).
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Tuple

Coord = Tuple[int, int]


class AgentStatus(Enum):
    EVACUATING = "evacuating"
    SAFE = "safe"
    DEAD = "dead"


class Agent:
    def __init__(self, agent_id: int, start: Coord, algorithm: str):
        self.id                 = agent_id
        self.pos                = start
        self.algorithm          = algorithm  # nombre del algoritmo que usa este agente
        self.status             = AgentStatus.EVACUATING
        self.path: List[Coord]  = []
        self.turns_taken        = 0

    def assign_path(self, path: Optional[List[Coord]]) -> None:
        self.path = path or []

    def next_move(self) -> Coord:
        """Devuelve la siguiente celda del plan, o la posición actual
        (acción 'esperar') si no hay plan o el plan está vacío."""
        if not self.path:
            return self.pos
        return self.path[0]

    def advance(self, new_pos: Coord) -> None:
        self.pos = new_pos
        self.turns_taken += 1
        if self.path and self.path[0] == new_pos:
            self.path.pop(0)

    def mark_dead(self) -> None:
        self.status = AgentStatus.DEAD

    def mark_safe(self) -> None:
        self.status = AgentStatus.SAFE

    def is_active(self) -> bool:
        return self.status == AgentStatus.EVACUATING
