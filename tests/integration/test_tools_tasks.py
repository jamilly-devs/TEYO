import pytest

from tools.errors import ToolNotFoundError, ToolValidationError
from tools.tasks import complete_task, create_task, delete_task, list_tasks, update_task


def test_create_task_requires_title(db_session, user_id):
    with pytest.raises(ToolValidationError):
        create_task(db_session, user_id, {})


def test_create_task_persists_and_returns_id(db_session, user_id):
    result = create_task(db_session, user_id, {"title": "estudar inglês"})
    assert result["id"] is not None
    assert result["title"] == "estudar inglês"
    assert result["status"] == "pending"
    assert result["priority"] == "medium"


def test_create_task_rejects_goal_from_another_user(db_session, user_id, other_user_id):
    from tools.goals import create_goal

    other_goal = create_goal(db_session, other_user_id, {"title": "meta alheia"})
    with pytest.raises(ToolNotFoundError):
        create_task(db_session, user_id, {"title": "x", "goal_id": other_goal["id"]})


def test_update_task_requires_task_id(db_session, user_id):
    with pytest.raises(ToolValidationError):
        update_task(db_session, user_id, {"title": "novo título"})


def test_update_task_rejects_unresolved_or_foreign_task_id(db_session, user_id, other_user_id):
    with pytest.raises(ToolNotFoundError):
        update_task(db_session, user_id, {"task_id": 999, "title": "x"})

    foreign = create_task(db_session, other_user_id, {"title": "tarefa alheia"})
    with pytest.raises(ToolNotFoundError):
        update_task(db_session, user_id, {"task_id": foreign["id"], "title": "x"})


def test_update_task_changes_fields(db_session, user_id):
    task = create_task(db_session, user_id, {"title": "x"})
    result = update_task(db_session, user_id, {"task_id": task["id"], "priority": "high"})
    assert result["priority"] == "high"


def test_delete_task_removes_it(db_session, user_id):
    task = create_task(db_session, user_id, {"title": "x"})
    result = delete_task(db_session, user_id, {"task_id": task["id"]})
    assert result == {"deleted": True, "task_id": task["id"]}
    assert list_tasks(db_session, user_id, {})["items"] == []


def test_delete_task_missing_id_does_not_execute(db_session, user_id):
    with pytest.raises(ToolValidationError):
        delete_task(db_session, user_id, {})


def test_complete_task_marks_done_without_gamification_fields(db_session, user_id):
    task = create_task(db_session, user_id, {"title": "x"})
    result = complete_task(db_session, user_id, {"task_id": task["id"]})
    assert result["status"] == "done"
    # FASE 5 não implementa gamificação/mascote (FASE 9) — o retorno da
    # tool não deve trazer nenhum campo relacionado a XP/mascote.
    assert "xp" not in result
    assert "mascot_state" not in result


def test_list_tasks_only_returns_owner_tasks(db_session, user_id, other_user_id):
    create_task(db_session, user_id, {"title": "minha"})
    create_task(db_session, other_user_id, {"title": "alheia"})

    result = list_tasks(db_session, user_id, {})
    assert [t["title"] for t in result["items"]] == ["minha"]
