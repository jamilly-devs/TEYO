"""Integração: conclusão de tarefa → XP, pelos QUATRO caminhos que a
FASE 8 unificou em `core.task_completion`. A gamificação se liga só ao
gancho `on_task_completed` (via `gamification.subscribers`), nunca
espalhada em tools/routers."""

from db.models.gamification import GamificationEvent, GamificationState
from gamification import config
from tools.tasks import complete_task as complete_task_tool
from tools.tasks import create_task as create_task_tool
from tools.tasks import update_task as update_task_tool


def _xp(db, user_id: int) -> int:
    state = db.get(GamificationState, user_id)
    return state.xp_total if state is not None else 0


def test_tool_complete_task_credits_xp_once(db_session, user_id):
    task = create_task_tool(db_session, user_id, {"title": "x"})

    complete_task_tool(db_session, user_id, {"task_id": task["id"]})
    complete_task_tool(db_session, user_id, {"task_id": task["id"]})  # idempotente

    assert _xp(db_session, user_id) == config.XP_TASK_COMPLETED
    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="task_completed")
        .count()
        == 1
    )


def test_tool_update_task_status_done_credits_xp_once(db_session, user_id):
    task = create_task_tool(db_session, user_id, {"title": "x"})

    update_task_tool(db_session, user_id, {"task_id": task["id"], "status": "done"})
    update_task_tool(db_session, user_id, {"task_id": task["id"], "status": "done"})

    assert _xp(db_session, user_id) == config.XP_TASK_COMPLETED


def test_tool_high_effort_completion_adds_bonus(db_session, user_id):
    task = create_task_tool(db_session, user_id, {"title": "x", "priority": "high"})

    complete_task_tool(db_session, user_id, {"task_id": task["id"]})

    assert _xp(db_session, user_id) == (
        config.XP_TASK_COMPLETED + config.XP_TASK_HIGH_EFFORT_BONUS
    )


def test_rest_complete_endpoint_credits_xp(authenticated_client, client_db_session):
    task = authenticated_client.post("/tasks", json={"title": "x"}).json()

    authenticated_client.post(f"/tasks/{task['id']}/complete")

    state = client_db_session.get(GamificationState, 1)
    assert state is not None and state.xp_total == config.XP_TASK_COMPLETED


def test_rest_patch_status_done_credits_xp(authenticated_client, client_db_session):
    task = authenticated_client.post("/tasks", json={"title": "x"}).json()

    authenticated_client.patch(f"/tasks/{task['id']}", json={"status": "done"})

    state = client_db_session.get(GamificationState, 1)
    assert state is not None and state.xp_total == config.XP_TASK_COMPLETED
