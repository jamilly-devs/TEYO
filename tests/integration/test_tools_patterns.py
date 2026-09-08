from datetime import datetime, timedelta

from db.models.enums import TaskCategory, TaskStatus
from db.models.task import Task
from tools.patterns import get_patterns, get_routine_changes, select_relevant_patterns

NOW = datetime(2026, 9, 7, 12, 0, 0)


def _at(days_ago: int, hour: int) -> datetime:
    return (NOW - timedelta(days=days_ago)).replace(hour=hour, minute=0, second=0, microsecond=0)


def _completed_task(db, user_id, category, when):
    task = Task(user_id=user_id, title="x", category=category, status=TaskStatus.DONE, updated_at=when)
    db.add(task)
    db.commit()
    return task


def _seed_active_house_pattern(db, user_id):
    for i in range(15):
        _completed_task(db, user_id, TaskCategory.HOUSE, _at(8 + (i % 14), 20))
    for offset in (20, 15, 10):
        _completed_task(db, user_id, TaskCategory.HOUSE, _at(offset, 8))


def _seed_deprecated_studies_pattern_with_recent_change(db, user_id):
    for i in range(24):
        _completed_task(db, user_id, TaskCategory.STUDIES, _at(8 + (i % 14), 20))
    for offset in (1, 2, 3, 4, 5, 6):
        _completed_task(db, user_id, TaskCategory.STUDIES, _at(offset, 8))
    _completed_task(db, user_id, TaskCategory.STUDIES, _at(7, 20))


def _seed_candidate_general_pattern(db, user_id):
    for offset in range(5):
        _completed_task(db, user_id, TaskCategory.GENERAL, _at(offset + 10, 20))
    for offset in range(5):
        _completed_task(db, user_id, TaskCategory.GENERAL, _at(offset + 1, 8))


def test_get_patterns_without_filter_returns_only_active(db_session, user_id, monkeypatch):
    _patch_now(monkeypatch)
    _seed_active_house_pattern(db_session, user_id)
    _seed_candidate_general_pattern(db_session, user_id)

    result = get_patterns(db_session, user_id, {})

    statuses = {item["status"] for item in result["items"]}
    assert statuses == {"active"}
    assert result["items"][0]["category"] == "house"


def test_get_patterns_with_pattern_type_also_returns_candidate(db_session, user_id, monkeypatch):
    _patch_now(monkeypatch)
    _seed_candidate_general_pattern(db_session, user_id)

    result = get_patterns(db_session, user_id, {"pattern_type": "task_time_of_day:general"})

    assert [item["status"] for item in result["items"]] == ["candidate"]


def test_get_patterns_never_returns_deprecated(db_session, user_id, monkeypatch):
    _patch_now(monkeypatch)
    _seed_deprecated_studies_pattern_with_recent_change(db_session, user_id)

    result = get_patterns(db_session, user_id, {"pattern_type": "task_time_of_day:studies"})
    assert result["items"] == []


def test_get_patterns_flags_routine_changes_detected_even_with_empty_items(
    db_session, user_id, monkeypatch
):
    """Auditoria FASE 7: um padrão despromovido por divergência sustentada
    some de `items`, mas `routine_changes_detected` precisa continuar
    `true` para que o LLM nunca conclua "não há padrão/mudança" só por
    causa de uma lista vazia (ver PATTERN_ENGINE.md, TOOLS.md)."""
    _patch_now(monkeypatch)
    _seed_deprecated_studies_pattern_with_recent_change(db_session, user_id)

    result = get_patterns(db_session, user_id, {"pattern_type": "task_time_of_day:studies"})
    assert result["items"] == []
    assert result["routine_changes_detected"] is True


def test_get_patterns_routine_changes_detected_is_false_with_no_divergence(
    db_session, user_id, monkeypatch
):
    _patch_now(monkeypatch)
    _seed_active_house_pattern(db_session, user_id)

    result = get_patterns(db_session, user_id, {})
    assert result["items"] != []
    assert result["routine_changes_detected"] is False


def test_get_routine_changes_only_returns_diverging_patterns(db_session, user_id, monkeypatch):
    _patch_now(monkeypatch)
    _seed_active_house_pattern(db_session, user_id)
    _seed_deprecated_studies_pattern_with_recent_change(db_session, user_id)

    result = get_routine_changes(db_session, user_id, {})

    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["category"] == "studies"
    assert item["recent_change"] is True
    assert item["recent_change_confidence"] is not None


def test_select_relevant_patterns_includes_active_description_and_change_line(
    db_session, user_id, monkeypatch
):
    _patch_now(monkeypatch)
    _seed_active_house_pattern(db_session, user_id)
    _seed_deprecated_studies_pattern_with_recent_change(db_session, user_id)

    lines = select_relevant_patterns(db_session, user_id)

    assert any("house" in line for line in lines)
    assert any("Possível mudança" in line and "studies" in line for line in lines)


def test_select_relevant_patterns_is_empty_with_no_history(db_session, user_id, monkeypatch):
    _patch_now(monkeypatch)
    assert select_relevant_patterns(db_session, user_id) == []


def _patch_now(monkeypatch):
    """As funções de `tools/patterns.py` chamam `refresh_patterns_for_user`
    sem `now` explícito (assinatura real do Orquestrador/tools) — trava
    `datetime.utcnow()` do módulo do motor para o mesmo instante de
    referência usado ao gerar os dados de teste."""
    import pattern_engine.task_time_of_day as engine

    class _FixedDatetime(datetime):
        @classmethod
        def utcnow(cls):
            return NOW

    monkeypatch.setattr(engine, "datetime", _FixedDatetime)
