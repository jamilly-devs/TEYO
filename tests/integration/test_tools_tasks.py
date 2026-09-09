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


def test_complete_task_fires_domain_hook(db_session, user_id, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "core.task_completion.on_task_completed",
        lambda db, uid, task: calls.append((uid, task.id)),
    )
    task = create_task(db_session, user_id, {"title": "x"})

    complete_task(db_session, user_id, {"task_id": task["id"]})

    assert calls == [(user_id, task["id"])]


def test_update_task_to_done_fires_domain_hook_once(db_session, user_id, monkeypatch):
    # `update_task` com status=done é um dos quatro caminhos de conclusão —
    # passa pelo mesmo ponto único; e não redispara numa tarefa já done.
    calls = []
    monkeypatch.setattr(
        "core.task_completion.on_task_completed",
        lambda db, uid, task: calls.append(task.id),
    )
    task = create_task(db_session, user_id, {"title": "x"})

    first = update_task(db_session, user_id, {"task_id": task["id"], "status": "done"})
    update_task(db_session, user_id, {"task_id": task["id"], "status": "done"})

    assert first["status"] == "done"
    assert calls == [task["id"]]


def test_update_task_without_status_change_does_not_fire_hook(db_session, user_id, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "core.task_completion.on_task_completed",
        lambda db, uid, task: calls.append(task.id),
    )
    task = create_task(db_session, user_id, {"title": "x"})

    update_task(db_session, user_id, {"task_id": task["id"], "priority": "high"})

    assert calls == []


def test_list_tasks_only_returns_owner_tasks(db_session, user_id, other_user_id):
    create_task(db_session, user_id, {"title": "minha"})
    create_task(db_session, other_user_id, {"title": "alheia"})

    result = list_tasks(db_session, user_id, {})
    assert [t["title"] for t in result["items"]] == ["minha"]
