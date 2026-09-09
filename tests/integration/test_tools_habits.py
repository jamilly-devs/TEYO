import pytest

from tools.errors import ToolNotFoundError, ToolValidationError
from tools.habits import create_habit, list_habits, log_habit, update_habit


def test_create_requires_title_and_frequency(db_session, user_id):
    with pytest.raises(ToolValidationError):
        create_habit(db_session, user_id, {"title": "ler"})
    with pytest.raises(ToolValidationError):
        create_habit(db_session, user_id, {"title": "ler", "frequency_target": 9})


def test_create_and_list_with_streak(db_session, user_id):
    result = create_habit(db_session, user_id, {"title": "ler", "frequency_target": 3})
    assert result["id"] is not None
    assert result["streak"] == 0

    listed = list_habits(db_session, user_id, {})
    assert [h["title"] for h in listed["items"]] == ["ler"]


def test_update_habit(db_session, user_id):
    habit = create_habit(db_session, user_id, {"title": "ler", "frequency_target": 3})
    updated = update_habit(
        db_session, user_id, {"habit_id": habit["id"], "frequency_target": 5}
    )
    assert updated["frequency_target"] == 5


def test_log_habit_idempotent_per_day(db_session, user_id):
    habit = create_habit(db_session, user_id, {"title": "ler", "frequency_target": 3})

    first = log_habit(db_session, user_id, {"habit_id": habit["id"]})
    second = log_habit(db_session, user_id, {"habit_id": habit["id"]})

    assert first["already_logged_today"] is False
    assert second["already_logged_today"] is True


def test_log_habit_missing_id_is_rejected(db_session, user_id):
    with pytest.raises(ToolValidationError):
        log_habit(db_session, user_id, {})


def test_operations_scoped_to_owner(db_session, user_id, other_user_id):
    habit = create_habit(db_session, other_user_id, {"title": "ler", "frequency_target": 3})
    with pytest.raises(ToolNotFoundError):
        log_habit(db_session, user_id, {"habit_id": habit["id"]})
    with pytest.raises(ToolNotFoundError):
        update_habit(db_session, user_id, {"habit_id": habit["id"], "title": "x"})
