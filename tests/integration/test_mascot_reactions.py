"""Mascote reagindo a eventos de domínio (via subscribers registrados por
backend/bootstrap.py — importado no conftest)."""

from datetime import datetime

from core import domain_events
from db.models.enums import TaskPriority, TaskStatus
from db.models.mascot import MascotState
from db.models.task import Task
from gamification import engine as gami_engine
from mascot import engine as mascot_engine
from tools.planner import reorganize_day


def _done_task(db, user_id, priority=TaskPriority.MEDIUM):
    task = Task(user_id=user_id, title="t", status=TaskStatus.DONE, priority=priority)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def test_task_completed_sets_happy(db_session, user_id):
    domain_events.on_task_completed(db_session, user_id, _done_task(db_session, user_id))
    db_session.commit()
    assert mascot_engine.resolve_state(db_session, user_id)["current_expression"] == "happy"


def test_high_effort_task_completed_sets_proud(db_session, user_id):
    task = _done_task(db_session, user_id, priority=TaskPriority.HIGH)
    domain_events.on_task_completed(db_session, user_id, task)
    db_session.commit()
    assert mascot_engine.resolve_state(db_session, user_id)["current_expression"] == "proud"


def test_low_energy_hook_sets_caring(db_session, user_id):
    domain_events.on_low_energy_reported(db_session, user_id)
    db_session.commit()
    assert mascot_engine.resolve_state(db_session, user_id)["current_expression"] == "caring"


def test_reorganize_day_tool_low_energy_persists_caring(db_session, user_id):
    reorganize_day(db_session, user_id, {"energy_level": "low"})  # commita internamente
    assert db_session.get(MascotState, user_id).current_expression == "caring"


def test_reorganize_endpoint_low_energy_persists_caring(
    authenticated_client, client_db_session
):
    authenticated_client.post("/planner/reorganize", json={"energy_level": "low"})
    assert client_db_session.get(MascotState, 1).current_expression == "caring"


def test_level_up_bumps_stage_and_expression(db_session, user_id):
    # 200 XP -> nível 3 -> estágio 2 (DECISÃO C)
    gami_engine.award_xp(db_session, user_id, "manual", 200, now=datetime(2026, 9, 9, 12, 0, 0))
    db_session.commit()

    state = mascot_engine.resolve_state(db_session, user_id)
    assert state["evolution_stage"] == 2
    assert state["current_expression"] == "proud"
