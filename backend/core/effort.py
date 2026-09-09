"""Heurística de "tarefa de maior esforço".

Extraída de `planner/daily_plan.py` (efeito de `energy_level="low"` em
`reorganize_day`) para ser reutilizável. DECIDIDO com Jams (FASE 8,
Opção A de PLANNER.md): não existe estimativa de duração/esforço no
schema de `tasks`, então "maior esforço" é só o que já existe — prioridade
alta e/ou Pomodoro habilitado. Nenhuma métrica nova é inventada aqui.

A FASE 9 (GAMIFICATION.md: "foco total", Pomodoro, produtividade) tende a
querer o mesmo conceito; manter uma única função evita duas definições de
esforço divergentes."""

from typing import Optional

from db.models.enums import TaskPriority
from db.models.task import Task


def is_high_effort(
    *, priority: Optional[TaskPriority], pomodoro_enabled: Optional[bool]
) -> bool:
    return priority == TaskPriority.HIGH or bool(pomodoro_enabled)


def is_high_effort_task(task: Task) -> bool:
    return is_high_effort(priority=task.priority, pomodoro_enabled=task.pomodoro_enabled)
