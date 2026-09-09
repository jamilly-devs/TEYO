"""core/domain_events.py — os ganchos da FASE 8 agora distribuem para os
subscribers registrados (FASE 9). Continuam com as mesmas assinaturas e
sem `commit`. A mudança de "sem efeito" (FASE 8) para "dispara
gamificação/mascote" (FASE 9) é deliberada — ver DOCUMENTATION_AUDIT.md."""

import logging
from datetime import datetime

from core.domain_events import (
    on_low_energy_reported,
    on_pomodoro_completed,
    on_task_completed,
)
from db.models.enums import PomodoroStatus, TaskStatus
from db.models.gamification import GamificationEvent, GamificationState
from db.models.pomodoro import PomodoroSession
from db.models.task import Task


def _task(db, user_id) -> Task:
    task = Task(user_id=user_id, title="t", status=TaskStatus.PENDING)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def _pomodoro(db, user_id) -> PomodoroSession:
    session = PomodoroSession(
        user_id=user_id, status=PomodoroStatus.COMPLETED, started_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def test_task_completed_hook_drives_gamification(db_session, user_id):
    task = _task(db_session, user_id)

    on_task_completed(db_session, user_id, task)
    db_session.commit()

    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="task_completed")
        .count()
        == 1
    )
    assert db_session.get(GamificationState, user_id) is not None


def test_pomodoro_completed_hook_drives_gamification(db_session, user_id):
    session = _pomodoro(db_session, user_id)

    on_pomodoro_completed(db_session, user_id, session)
    db_session.commit()

    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="pomodoro_completed")
        .count()
        == 1
    )


def test_low_energy_hook_does_not_award_xp(db_session, user_id):
    on_low_energy_reported(db_session, user_id)
    db_session.commit()

    assert db_session.query(GamificationEvent).filter_by(user_id=user_id).count() == 0


def test_hooks_still_log_the_event(db_session, user_id, caplog):
    task = _task(db_session, user_id)
    with caplog.at_level(logging.INFO, logger="core.domain_events"):
        on_task_completed(db_session, user_id, task)
        on_low_energy_reported(db_session, user_id)

    messages = " ".join(record.message for record in caplog.records)
    assert "task_completed" in messages
    assert "low_energy_reported" in messages
