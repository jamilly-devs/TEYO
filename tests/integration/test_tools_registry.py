import pytest

from tools.errors import UnknownToolError
from tools.registry import default_tool_registry


def test_unknown_tool_is_rejected_without_executing_anything(db_session, user_id):
    registry = default_tool_registry()
    with pytest.raises(UnknownToolError):
        registry.execute(db_session, user_id, "delete_everything", {})


def test_registry_exposes_a_spec_for_every_registered_tool():
    registry = default_tool_registry()
    names = {spec.name for spec in registry.specs()}
    assert names == {
        "create_task",
        "update_task",
        "delete_task",
        "complete_task",
        "list_tasks",
        "create_event",
        "update_event",
        "delete_event",
        "list_events",
        "create_goal",
        "update_goal",
        "list_goals",
        "add_market_item",
        "remove_market_item",
        "list_market_items",
        "create_financial_record",
        "list_financial_records",
    }


@pytest.mark.parametrize(
    "name", ["delete_task", "delete_event", "remove_market_item"]
)
def test_destructive_actions_are_flagged_for_confirmation(name):
    """BUSINESS_RULES.md #4: ações destrutivas exigem confirmação explícita
    do usuário antes da execução — a tool fica marcada para reforçar isso
    na descrição enviada ao LLM."""
    registry = default_tool_registry()
    assert registry.is_destructive(name) is True


@pytest.mark.parametrize(
    "name",
    [
        "create_task",
        "update_task",
        "complete_task",
        "list_tasks",
        "create_event",
        "update_event",
        "list_events",
        "create_goal",
        "update_goal",
        "list_goals",
        "add_market_item",
        "list_market_items",
        "create_financial_record",
        "list_financial_records",
    ],
)
def test_non_destructive_actions_are_not_flagged(name):
    registry = default_tool_registry()
    assert registry.is_destructive(name) is False
