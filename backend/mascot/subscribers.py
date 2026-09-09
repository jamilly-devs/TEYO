"""Liga o mascote aos eventos de domínio.

Eventos crus (`task_completed`, `low_energy_reported`) e derivados da
gamificação (`level_up`, `achievement_unlocked`). Como `gamification.
subscribers` é registrado antes (ver `backend/bootstrap.py`), quando um
`level_up`/`achievement_unlocked` acontece durante a mesma conclusão de
tarefa ele já chega aqui com nível/conquista persistidos.

Nota (V1): "último evento vence" para a expressão — se uma conclusão de
tarefa também sobe de nível, a expressão final pode ser `happy` em vez de
`proud`; o TTL traz de volta a `idle`. Registrado em DOCUMENTATION_AUDIT.md.
"""

from core import domain_events
from core.effort import is_high_effort_task
from mascot import engine


def _on_task_completed(*, db, user_id, task, **_):
    engine.set_expression(db, user_id, "proud" if is_high_effort_task(task) else "happy")


def _on_low_energy_reported(*, db, user_id, **_):
    engine.set_expression(db, user_id, "caring")


def _on_level_up(*, db, user_id, to_level, **_):
    engine.recompute_stage(db, user_id, to_level)
    engine.set_expression(db, user_id, "proud")


def _on_achievement_unlocked(*, db, user_id, **_):
    engine.set_expression(db, user_id, "celebrating")


domain_events.subscribe(domain_events.TASK_COMPLETED, _on_task_completed)
domain_events.subscribe(domain_events.LOW_ENERGY_REPORTED, _on_low_energy_reported)
domain_events.subscribe(domain_events.LEVEL_UP, _on_level_up)
domain_events.subscribe(domain_events.ACHIEVEMENT_UNLOCKED, _on_achievement_unlocked)
