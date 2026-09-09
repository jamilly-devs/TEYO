"""on_pomodoro_completed -> gamificação.

Decisão FASE 9: NÃO criar módulo de Pomodoro. `pomodoro_sessions` segue
sem produtor de produção; o caminho é exercitado chamando o gancho de
domínio direto, como um produtor futuro faria."""

from datetime import datetime

from core import domain_events
from db.models.achievement import Achievement
from db.models.enums import PomodoroStatus
from db.models.gamification import GamificationEvent, GamificationState
from db.models.pomodoro import PomodoroSession
from gamification import config


def _completed_session(db, user_id) -> PomodoroSession:
    session = PomodoroSession(
        user_id=user_id,
        status=PomodoroStatus.COMPLETED,
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def test_pomodoro_completed_hook_awards_xp_and_unlocks_first_focus(db_session, user_id):
    domain_events.on_pomodoro_completed(
        db_session, user_id, _completed_session(db_session, user_id)
    )
    db_session.commit()

    state = db_session.get(GamificationState, user_id)
    assert state.xp_total == config.XP_POMODORO_COMPLETED + config.XP_ACHIEVEMENT_UNLOCKED
    assert (
        db_session.query(Achievement)
        .filter_by(user_id=user_id, code="pomodoro_1")
        .count()
        == 1
    )
    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="pomodoro_completed")
        .count()
        == 1
    )


def test_pomodoro_hook_isolated_by_user(db_session, user_id, other_user_id):
    domain_events.on_pomodoro_completed(
        db_session, other_user_id, _completed_session(db_session, other_user_id)
    )
    db_session.commit()
    assert db_session.get(GamificationState, user_id) is None
