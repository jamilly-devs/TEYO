import pytest

from tools.errors import ToolNotFoundError, ToolValidationError
from tools.events import create_event, delete_event, list_events, update_event

_VALID = {"title": "reunião", "start_at": "2026-09-10T14:00:00", "end_at": "2026-09-10T15:00:00"}


def test_create_event_requires_title_start_and_end(db_session, user_id):
    with pytest.raises(ToolValidationError):
        create_event(db_session, user_id, {})
    with pytest.raises(ToolValidationError):
        create_event(db_session, user_id, {"title": "x"})


def test_create_event_via_tool_is_tagged_as_teyo_nlu(db_session, user_id):
    result = create_event(db_session, user_id, _VALID)
    assert result["source"] == "teyo_nlu"


def test_update_event_requires_event_id(db_session, user_id):
    with pytest.raises(ToolValidationError):
        update_event(db_session, user_id, {"title": "y"})


def test_update_event_rejects_foreign_event(db_session, user_id, other_user_id):
    foreign = create_event(db_session, other_user_id, _VALID)
    with pytest.raises(ToolNotFoundError):
        update_event(db_session, user_id, {"event_id": foreign["id"], "title": "y"})


def test_delete_event_removes_it(db_session, user_id):
    event = create_event(db_session, user_id, _VALID)
    result = delete_event(db_session, user_id, {"event_id": event["id"]})
    assert result == {"deleted": True, "event_id": event["id"]}
    assert list_events(db_session, user_id, {})["items"] == []


def test_list_events_only_returns_owner_events(db_session, user_id, other_user_id):
    create_event(db_session, user_id, _VALID)
    create_event(db_session, other_user_id, _VALID)
    assert len(list_events(db_session, user_id, {})["items"]) == 1


# --- FASE 8: sobreposição de horário (MODULES/AGENDA.md, PLANNER.md) -------


def test_create_event_signals_conflict_instead_of_creating(db_session, user_id):
    create_event(db_session, user_id, _VALID)
    overlapping = {
        "title": "outra reunião",
        "start_at": "2026-09-10T14:30:00",
        "end_at": "2026-09-10T15:30:00",
    }

    result = create_event(db_session, user_id, overlapping)

    assert result["conflict"] is True
    assert len(result["conflicting_events"]) == 1
    assert len(list_events(db_session, user_id, {})["items"]) == 1


def test_create_event_with_confirm_overlap_creates_despite_conflict(db_session, user_id):
    create_event(db_session, user_id, _VALID)
    overlapping = {
        "title": "outra reunião",
        "start_at": "2026-09-10T14:30:00",
        "end_at": "2026-09-10T15:30:00",
        "confirm_overlap": True,
    }

    result = create_event(db_session, user_id, overlapping)

    assert "conflict" not in result
    assert result["title"] == "outra reunião"
    assert len(list_events(db_session, user_id, {})["items"]) == 2


def test_create_event_without_overlap_never_signals_conflict(db_session, user_id):
    create_event(db_session, user_id, _VALID)
    non_overlapping = {
        "title": "depois",
        "start_at": "2026-09-10T16:00:00",
        "end_at": "2026-09-10T17:00:00",
    }

    result = create_event(db_session, user_id, non_overlapping)

    assert "conflict" not in result
    assert len(list_events(db_session, user_id, {})["items"]) == 2


def test_update_event_signals_conflict_when_new_time_overlaps_another(db_session, user_id):
    first = create_event(db_session, user_id, _VALID)
    second = create_event(
        db_session,
        user_id,
        {"title": "livre", "start_at": "2026-09-10T16:00:00", "end_at": "2026-09-10T17:00:00"},
    )

    result = update_event(
        db_session, user_id, {"event_id": second["id"], "start_at": first["start_at"]}
    )

    assert result["conflict"] is True
    unchanged = [e for e in list_events(db_session, user_id, {})["items"] if e["id"] == second["id"]][0]
    assert unchanged["start_at"] == second["start_at"]


def test_update_event_without_time_change_never_checks_conflict(db_session, user_id):
    first = create_event(db_session, user_id, _VALID)
    create_event(
        db_session,
        user_id,
        {"title": "livre", "start_at": "2026-09-10T16:00:00", "end_at": "2026-09-10T17:00:00"},
    )

    result = update_event(db_session, user_id, {"event_id": first["id"], "title": "renomeada"})

    assert "conflict" not in result
    assert result["title"] == "renomeada"
