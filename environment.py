"""
environment.py
---------------
Motor de simulación por turnos. Cada turno:

  1. Cada agente activo replanifica su ruta con el algoritmo asignado
     (porque el fuego pudo haber bloqueado su plan anterior, o la
     congestión cambió los costos).
  2. Cada agente da UN paso (o espera).
  3. Se registra la ocupación de la celda para penalizar congestión
     en el siguiente turno.
  4. El fuego se propaga cada `spread_interval` turnos.
  5. Se revisa qué agentes murieron (fuego los alcanzó) o llegaron a
     la salida.

La simulación termina cuando todos los agentes están SAFE o DEAD, o
al alcanzar `max_turns` (para evitar loops infinitos si alguien queda
atrapado).
"""

from __future__ import annotations
from typing import Callable, Dict, List, Tuple

from grid import Grid
from fire import FireSpreader
from agent import Agent, AgentStatus

Coord = Tuple[int, int]
SearchFn = Callable[[Grid, Coord, List[Coord]], List[Coord]]


class SimulationResult:
    def __init__(self):
        self.turns_to_clear: int = 0
        self.survivors: int = 0
        self.total_agents: int = 0
        self.survival_rate: float = 0.0
        self.per_agent_turns: List[int] = []  # solo de los que sobrevivieron

    def as_dict(self) -> dict:
        return {
            "turns_to_clear": self.turns_to_clear,
            "survivors": self.survivors,
            "total_agents": self.total_agents,
            "survival_rate": self.survival_rate,
            "per_agent_turns": self.per_agent_turns,
        }


class Simulation:
    def __init__(
        self,
        grid: Grid,
        agents: List[Agent],
        search_fn: SearchFn,
        fire_spread_interval: int = 3,
        max_turns: int = 500,
    ):
        self.grid = grid
        self.agents = agents
        self.search_fn = search_fn
        self.fire = FireSpreader(grid, grid.get_all_fires(), fire_spread_interval)
        self.max_turns = max_turns
        self.turn = 0

    def run(self) -> SimulationResult:
        while self.turn < self.max_turns and self._any_active():
            self.turn += 1
            self._replan_all()
            self._step_all()
            self.fire.tick()
            self._resolve_fire_casualties()

        return self._build_result()

    # ------------------------------------------------------------------
    def _any_active(self) -> bool:
        return any(a.is_active() for a in self.agents)

    def _replan_all(self) -> None:
        for a in self.agents:
            if a.is_active():
                path = self.search_fn(self.grid, a.pos, self.grid.exits)
                a.assign_path(path)

    def _step_all(self) -> None:
        self.grid.clear_occupancy()
        active = [a for a in self.agents if a.is_active()]
        cap = self.grid.capacity_per_cell
        count = {}
        for a in active:
            count[a.pos] = count.get(a.pos, 0) + 1

        for a in active:
            target = a.next_move()
            free = target in self.grid.exits or count.get(target, 0) < cap
            if target != a.pos and self.grid.is_walkable(target) and free:
                count[a.pos] -= 1
                count[target] = count.get(target, 0) + 1
                a.advance(target)
            else:
                a.turns_taken += 1  # waiting still costs a turn
            self.grid.add_occupancy(a.pos)
            if a.pos in self.grid.exits:
                a.mark_safe()
                count[a.pos] -= 1

    def _resolve_fire_casualties(self) -> None:
        for a in self.agents:
            if a.is_active() and self.fire.reached(a.pos):
                a.mark_dead()

    def _build_result(self) -> SimulationResult:
        result = SimulationResult()
        result.total_agents = len(self.agents)
        result.survivors = sum(1 for a in self.agents if a.status == AgentStatus.SAFE)
        result.survival_rate = result.survivors / result.total_agents if result.total_agents else 0.0
        result.per_agent_turns = [a.turns_taken for a in self.agents if a.status == AgentStatus.SAFE]
        result.turns_to_clear = max(result.per_agent_turns) if result.per_agent_turns else self.turn
        return result
