"""core/pomodoro_completion.py — ponto único de conclusão (FASE 10, DT-4).

Sessão válida (>= MIN_VALID_MINUTES decorridos) dispara
`on_pomodoro_completed`; sessão curta demais não; sessão já concluída é
no-op. Não commita."""

from datetime import datetime, timedelta

from core.pomodoro_completion import MIN_VALID_MINUTES, complete_session
from db.models.enums import PomodoroStatus
from db.models.gamification import GamificationEvent
from db.models.pomodoro import PomodoroSession

NOW = datetime(2026, 9, 9, 12, 0, 0)


def _session(db, user_id, started_minutes_ago: float) -> PomodoroSession:
    session = PomodoroSession(
        user_id=user_id,
        status=PomodoroStatus.ACTIVE,
        started_at=NOW - timedelta(minutes=started_minutes_ago),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _pomodoro_events(db, user_id) -> int:
    return (
        db.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="pomodoro_completed")
        .count()
    )


def test_valid_session_fires_hook_and_awards_xp(db_session, user_id):
    session = _session(db_session, user_id, started_minutes_ago=25)

    fired = complete_session(db_session, user_id, session, now=NOW)
    db_session.commit()

    assert fired is True
    assert session.status == PomodoroStatus.COMPLETED
    assert session.ended_at == NOW
    assert _pomodoro_events(db_session, user_id) == 1


def test_short_session_completes_without_firing_hook(db_session, user_id):
    session = _session(db_session, user_id, started_minutes_ago=MIN_VALID_MINUTES / 2)

    fired = complete_session(db_session, user_id, session, now=NOW)
    db_session.commit()

    assert fired is False
    assert session.status == PomodoroStatus.COMPLETED
    assert _pomodoro_events(db_session, user_id) == 0


def test_completing_twice_is_idempotent(db_session, user_id):
    session = _session(db_session, user_id, started_minutes_ago=25)

    complete_session(db_session, user_id, session, now=NOW)
    second = complete_session(db_session, user_id, session, now=NOW)
    db_session.commit()

    assert second is False
    assert _pomodoro_events(db_session, user_id) == 1
