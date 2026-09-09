from datetime import datetime, timedelta

from db.models.enums import TaskPriority, TaskStatus
from db.models.task import Task
from tools.planner import get_daily_plan, reorganize_day

NOW = datetime(2026, 9, 7, 12, 0, 0)


def _task(db, user_id, title, priority=TaskPriority.MEDIUM, pomodoro_enabled=False):
    task = Task(
        user_id=user_id,
        title=title,
        priority=priority,
        status=TaskStatus.PENDING,
        pomodoro_enabled=pomodoro_enabled,
    )
    db.add(task)
    db.commit()
    return task


def test_get_daily_plan_returns_serialized_items(db_session, user_id):
    _task(db_session, user_id, "estudar", priority=TaskPriority.HIGH)

    result = get_daily_plan(db_session, user_id, {})

    assert "date" in result
    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["kind"] == "task"
    assert item["title"] == "estudar"
    assert item["priority"] == "high"
    assert item["reason"] is None


def test_get_daily_plan_is_isolated_by_user_id(db_session, user_id, other_user_id):
    _task(db_session, other_user_id, "de outro usuário", priority=TaskPriority.HIGH)

    result = get_daily_plan(db_session, user_id, {})

    assert result["items"] == []


def test_reorganize_day_low_energy_defers_high_priority_task(db_session, user_id):
    light = _task(db_session, user_id, "leve", priority=TaskPriority.LOW)
    heavy = _task(db_session, user_id, "pesada", priority=TaskPriority.HIGH)

    result = reorganize_day(db_session, user_id, {"energy_level": "low"})

    items_by_title = {item["title"]: item for item in result["items"]}
    assert items_by_title["leve"]["reason"] is None
    assert items_by_title["pesada"]["reason"] is not None
    assert items_by_title["pesada"]["suggested_due_date"] is not None
    titles = [item["title"] for item in result["items"]]
    assert titles.index("pesada") > titles.index("leve")


def test_reorganize_day_without_energy_level_matches_get_daily_plan(db_session, user_id):
    _task(db_session, user_id, "tarefa", priority=TaskPriority.HIGH)

    plan = get_daily_plan(db_session, user_id, {})
    reorganized = reorganize_day(db_session, user_id, {})

    assert reorganized["items"] == plan["items"]


def test_reorganize_day_return_keeps_tools_md_contract(db_session, user_id):
    # "serializer tipado, contrato intacto": os campos internos
    # energy_level/reorganized de DailyPlan NÃO podem vazar no retorno.
    _task(db_session, user_id, "pesada", priority=TaskPriority.HIGH)

    result = reorganize_day(db_session, user_id, {"energy_level": "low"})

    assert set(result) == {"date", "items"}
    assert set(result["items"][0]) == {
        "kind",
        "id",
        "title",
        "period",
        "start_at",
        "priority",
        "reason",
        "suggested_due_date",
    }


def test_reorganize_day_low_energy_emits_observable_signal(db_session, user_id, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "tools.planner.on_low_energy_reported", lambda db, uid: calls.append(uid)
    )
    _task(db_session, user_id, "pesada", priority=TaskPriority.HIGH)

    reorganize_day(db_session, user_id, {"energy_level": "low"})

    assert calls == [user_id]


def test_reorganize_day_non_low_energy_does_not_emit_signal(db_session, user_id, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "tools.planner.on_low_energy_reported", lambda db, uid: calls.append(uid)
    )
    _task(db_session, user_id, "pesada", priority=TaskPriority.HIGH)

    reorganize_day(db_session, user_id, {})
    reorganize_day(db_session, user_id, {"energy_level": "medium"})
    reorganize_day(db_session, user_id, {"energy_level": "high"})

    assert calls == []
