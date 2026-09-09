"""Liga o motor de gamificação aos ganchos de domínio da FASE 8.

O import deste módulo tem efeito colateral de registro (feito por
`backend/bootstrap.py`). Handlers aceitam `**_` para tolerar chaves extras
no payload do despachante sem quebrar.
"""

from core import domain_events
from gamification import engine


def _on_task_completed(*, db, user_id, task, **_):
    engine.apply_task_completed(db, user_id, task)


def _on_pomodoro_completed(*, db, user_id, session, **_):
    engine.apply_pomodoro_completed(db, user_id, session)


domain_events.subscribe(domain_events.TASK_COMPLETED, _on_task_completed)
domain_events.subscribe(domain_events.POMODORO_COMPLETED, _on_pomodoro_completed)
