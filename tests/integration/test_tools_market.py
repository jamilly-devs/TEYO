import pytest

from tools.errors import ToolNotFoundError, ToolValidationError
from tools.market import add_market_item, list_market_items, remove_market_item


def test_add_market_item_requires_name(db_session, user_id):
    with pytest.raises(ToolValidationError):
        add_market_item(db_session, user_id, {})


def test_add_market_item_defaults_status_active(db_session, user_id):
    result = add_market_item(db_session, user_id, {"name": "arroz"})
    assert result["status"] == "active"


def test_remove_market_item_is_a_hard_delete_not_a_status_change(db_session, user_id):
    """DECIDIDO (sincronizado nesta fase — ver DOCUMENTATION_AUDIT.md):
    remove_market_item exclui a linha, é diferente de marcar como
    'purchased'."""
    item = add_market_item(db_session, user_id, {"name": "café"})
    result = remove_market_item(db_session, user_id, {"item_id": item["id"]})
    assert result == {"deleted": True, "item_id": item["id"]}
    assert list_market_items(db_session, user_id, {})["items"] == []


def test_remove_market_item_requires_item_id(db_session, user_id):
    with pytest.raises(ToolValidationError):
        remove_market_item(db_session, user_id, {})


def test_remove_market_item_rejects_foreign_item(db_session, user_id, other_user_id):
    foreign = add_market_item(db_session, other_user_id, {"name": "alheio"})
    with pytest.raises(ToolNotFoundError):
        remove_market_item(db_session, user_id, {"item_id": foreign["id"]})


def test_list_market_items_only_returns_owner_items(db_session, user_id, other_user_id):
    add_market_item(db_session, user_id, {"name": "meu"})
    add_market_item(db_session, other_user_id, {"name": "alheio"})
    assert len(list_market_items(db_session, user_id, {})["items"]) == 1
