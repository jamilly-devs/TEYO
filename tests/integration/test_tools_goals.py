import pytest

from tools.errors import ToolNotFoundError, ToolValidationError
from tools.goals import create_goal, list_goals, update_goal


def test_create_goal_requires_title(db_session, user_id):
    with pytest.raises(ToolValidationError):
        create_goal(db_session, user_id, {})


def test_create_goal_defaults_status_active(db_session, user_id):
    result = create_goal(db_session, user_id, {"title": "aprender inglês"})
    assert result["status"] == "active"


def test_update_goal_requires_goal_id(db_session, user_id):
    with pytest.raises(ToolValidationError):
        update_goal(db_session, user_id, {"status": "completed"})


def test_update_goal_rejects_foreign_goal(db_session, user_id, other_user_id):
    foreign = create_goal(db_session, other_user_id, {"title": "meta alheia"})
    with pytest.raises(ToolNotFoundError):
        update_goal(db_session, user_id, {"goal_id": foreign["id"], "status": "completed"})


def test_update_goal_changes_status(db_session, user_id):
    goal = create_goal(db_session, user_id, {"title": "x"})
    result = update_goal(db_session, user_id, {"goal_id": goal["id"], "status": "completed"})
    assert result["status"] == "completed"


def test_list_goals_only_returns_owner_goals(db_session, user_id, other_user_id):
    create_goal(db_session, user_id, {"title": "minha"})
    create_goal(db_session, other_user_id, {"title": "alheia"})
    assert len(list_goals(db_session, user_id, {})["items"]) == 1
