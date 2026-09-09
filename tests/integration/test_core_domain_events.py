"""core/domain_events.py — ganchos onde a FASE 9 (Gamificação/Mascote) vai
se ligar. Na FASE 8 eles NÃO têm efeito: só registram log, não gravam
nada, não dão commit. Estes testes travam esse "sem efeito" para que a
FASE 9 seja uma mudança deliberada, não um acidente."""

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


def test_hooks_do_not_write_gamification_rows(db_session, user_id):
    task = _task(db_session, user_id)
    pomodoro = _pomodoro(db_session, user_id)

    on_task_completed(db_session, user_id, task)
    on_pomodoro_completed(db_session, user_id, pomodoro)
    on_low_energy_reported(db_session, user_id)
    db_session.commit()

    assert db_session.query(GamificationEvent).count() == 0
    assert db_session.query(GamificationState).count() == 0


def test_hooks_log_the_event(db_session, user_id, caplog):
    task = _task(db_session, user_id)
    with caplog.at_level(logging.INFO, logger="core.domain_events"):
        on_task_completed(db_session, user_id, task)
        on_low_energy_reported(db_session, user_id)

    messages = " ".join(record.message for record in caplog.records)
    assert "task_completed" in messages
    assert "low_energy_reported" in messages
