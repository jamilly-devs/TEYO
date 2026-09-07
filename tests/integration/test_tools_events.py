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
