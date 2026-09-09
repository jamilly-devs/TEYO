"""Endpoints de Pomodoro (MODULES/POMODORO.md, FASE 10). Máquina de
estados active/paused/completed; uma sessão em andamento por usuário
(DT-5); sessão curta não concede XP (DT-4); sem tool de LLM (DT-9)."""

from datetime import datetime, timedelta

from db.models.gamification import GamificationState
from db.models.pomodoro import PomodoroSession


def test_requires_authentication(client):
    assert client.post("/pomodoro/sessions", json={}).status_code == 401


def test_start_pause_resume_complete_flow(authenticated_client):
    started = authenticated_client.post("/pomodoro/sessions", json={})
    assert started.status_code == 201
    session_id = started.json()["id"]
    assert started.json()["status"] == "active"

    assert (
        authenticated_client.post(f"/pomodoro/sessions/{session_id}/pause").json()["status"]
        == "paused"
    )
    assert (
        authenticated_client.post(f"/pomodoro/sessions/{session_id}/resume").json()["status"]
        == "active"
    )
    completed = authenticated_client.post(f"/pomodoro/sessions/{session_id}/complete")
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["ended_at"] is not None


def test_only_one_active_session_at_a_time(authenticated_client):
    authenticated_client.post("/pomodoro/sessions", json={})
    second = authenticated_client.post("/pomodoro/sessions", json={})
    assert second.status_code == 409


def test_active_endpoint_returns_current_or_null(authenticated_client):
    assert authenticated_client.get("/pomodoro/sessions/active").json() is None
    authenticated_client.post("/pomodoro/sessions", json={})
    assert authenticated_client.get("/pomodoro/sessions/active").json()["status"] == "active"


def test_resume_active_session_is_rejected(authenticated_client):
    session_id = authenticated_client.post("/pomodoro/sessions", json={}).json()["id"]
    assert (
        authenticated_client.post(f"/pomodoro/sessions/{session_id}/resume").status_code
        == 409
    )


def test_session_for_another_users_task_is_rejected(client):
    client.post("/auth/register", json={"email": "a@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "a@x.com", "password": "s3cret!"})
    task = client.post("/tasks", json={"title": "t"}).json()
    client.post("/auth/logout")

    client.post("/auth/register", json={"email": "b@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "b@x.com", "password": "s3cret!"})
    assert (
        client.post("/pomodoro/sessions", json={"task_id": task["id"]}).status_code == 404
    )


def test_short_session_completion_does_not_award_xp(authenticated_client):
    session_id = authenticated_client.post("/pomodoro/sessions", json={}).json()["id"]
    # concluída imediatamente -> abaixo do mínimo -> sem XP
    authenticated_client.post(f"/pomodoro/sessions/{session_id}/complete")

    assert authenticated_client.get("/gamification/state").json()["xp_total"] == 0


def test_valid_session_completion_awards_xp(authenticated_client, client_db_session):
    session_id = authenticated_client.post("/pomodoro/sessions", json={}).json()["id"]
    # backdata o início para simular 25 min decorridos (o endpoint não
    # recebe `now`) — mesma técnica dos testes do Motor de Padrões.
    session = client_db_session.get(PomodoroSession, session_id)
    session.started_at = datetime.utcnow() - timedelta(minutes=25)
    client_db_session.commit()

    authenticated_client.post(f"/pomodoro/sessions/{session_id}/complete")

    state = client_db_session.get(GamificationState, 1)
    assert state is not None and state.xp_total >= 20
