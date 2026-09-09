"""Pomodoro ↔ Gamificação (FASE 10). Substitui o teste que chamava o gancho
direto (FASE 9). A conclusão via endpoint dispara `on_pomodoro_completed`
uma vez; a gamificação (FASE 9) credita `XP_POMODORO_COMPLETED` e
desbloqueia `pomodoro_1` — sem lógica de XP no módulo de Pomodoro."""

from datetime import datetime, timedelta

from db.models.achievement import Achievement
from db.models.gamification import GamificationEvent, GamificationState
from db.models.pomodoro import PomodoroSession
from gamification import config


def _complete_valid_session(authenticated_client, client_db_session) -> None:
    session_id = authenticated_client.post("/pomodoro/sessions", json={}).json()["id"]
    session = client_db_session.get(PomodoroSession, session_id)
    session.started_at = datetime.utcnow() - timedelta(minutes=25)
    client_db_session.commit()
    authenticated_client.post(f"/pomodoro/sessions/{session_id}/complete")


def test_completed_session_awards_pomodoro_xp_and_first_focus(
    authenticated_client, client_db_session
):
    _complete_valid_session(authenticated_client, client_db_session)

    state = client_db_session.get(GamificationState, 1)
    assert state.xp_total == (
        config.XP_POMODORO_COMPLETED + config.XP_ACHIEVEMENT_UNLOCKED
    )
    assert (
        client_db_session.query(GamificationEvent)
        .filter_by(user_id=1, event_type="pomodoro_completed")
        .count()
        == 1
    )
    assert (
        client_db_session.query(Achievement)
        .filter_by(user_id=1, code="pomodoro_1")
        .count()
        == 1
    )


def test_no_duplicate_xp_on_second_complete_call(authenticated_client, client_db_session):
    session_id = authenticated_client.post("/pomodoro/sessions", json={}).json()["id"]
    session = client_db_session.get(PomodoroSession, session_id)
    session.started_at = datetime.utcnow() - timedelta(minutes=25)
    client_db_session.commit()

    authenticated_client.post(f"/pomodoro/sessions/{session_id}/complete")
    authenticated_client.post(f"/pomodoro/sessions/{session_id}/complete")

    assert (
        client_db_session.query(GamificationEvent)
        .filter_by(user_id=1, event_type="pomodoro_completed")
        .count()
        == 1
    )
