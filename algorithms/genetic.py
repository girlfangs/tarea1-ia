"""
genetic.py
----------
PENDIENTE (siguiente etapa): algoritmo genético propio para
planificación de rutas bajo congestión + fuego dinámico.

Idea de diseño sugerida (a discutir):
- Cromosoma: secuencia de acciones {arriba, abajo, izq, der, esperar}
  de largo fijo (ej. 2x el largo del camino más corto conocido).
- Fitness: combina (a) si el agente llega a la salida, (b) turnos
  usados, (c) costo acumulado de congestión, (d) penalización fuerte
  si camina hacia fuego o fuera de la grilla.
- Selección: torneo. Cruce: un punto o uniforme sobre la secuencia de
  acciones. Mutación: cambiar una acción al azar con probabilidad p.
- Como el entorno es dinámico (el fuego se propagate), se recomienda
  re-evolucionar la población cada k turnos en vez de una sola vez al
  inicio (replanificación periódica, igual que se exige para BFS/A*).
"""

from grid import Grid  # noqa: F401  (se usará al implementar)


def genetic_algorithm(*args, **kwargs):
    raise NotImplementedError("Algoritmo genético: pendiente de implementación.")
