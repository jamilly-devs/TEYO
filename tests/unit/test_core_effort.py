"""core/effort.py — heurística de "tarefa de maior esforço" (DECIDIDO com
Jams, FASE 8, Opção A: prioridade alta e/ou Pomodoro habilitado; sem
inventar métrica de duração/esforço)."""

import pytest

from core.effort import is_high_effort, is_high_effort_task
from db.models.enums import TaskPriority
from db.models.task import Task


@pytest.mark.parametrize(
    "priority,pomodoro,expected",
    [
        (TaskPriority.HIGH, False, True),
        (TaskPriority.HIGH, True, True),
        (TaskPriority.MEDIUM, True, True),
        (TaskPriority.LOW, True, True),
        (TaskPriority.MEDIUM, False, False),
        (TaskPriority.LOW, False, False),
        (None, None, False),
    ],
)
def test_is_high_effort_truth_table(priority, pomodoro, expected):
    assert is_high_effort(priority=priority, pomodoro_enabled=pomodoro) is expected


def test_is_high_effort_task_reads_from_task_fields():
    heavy = Task(user_id=1, title="x", priority=TaskPriority.HIGH, pomodoro_enabled=False)
    light = Task(user_id=1, title="y", priority=TaskPriority.LOW, pomodoro_enabled=False)
    pomodoro = Task(user_id=1, title="z", priority=TaskPriority.LOW, pomodoro_enabled=True)

    assert is_high_effort_task(heavy) is True
    assert is_high_effort_task(light) is False
    assert is_high_effort_task(pomodoro) is True
