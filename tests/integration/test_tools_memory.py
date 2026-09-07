import pytest

from tools.errors import ToolNotFoundError, ToolValidationError
from tools.memory import (
    forget_memory,
    get_memory,
    get_user_preferences,
    remember_fact,
    remember_preference,
    select_relevant_context,
)


def test_remember_preference_requires_key_and_value(db_session, user_id):
    with pytest.raises(ToolValidationError):
        remember_preference(db_session, user_id, {})
    with pytest.raises(ToolValidationError):
        remember_preference(db_session, user_id, {"key": "horario_estudo"})


def test_remember_preference_persists_with_user_stated_source(db_session, user_id):
    result = remember_preference(
        db_session, user_id, {"key": "horario_estudo", "value": "à noite"}
    )
    assert result["category"] == "preference"
    assert result["source"] == "user_stated"
    assert result["value"] == "à noite"


def test_remember_preference_overwrites_existing_entry_with_same_key(db_session, user_id):
    first = remember_preference(db_session, user_id, {"key": "horario_estudo", "value": "à noite"})
    second = remember_preference(db_session, user_id, {"key": "horario_estudo", "value": "de manhã"})

    assert second["id"] == first["id"]
    assert second["value"] == "de manhã"

    result = get_user_preferences(db_session, user_id, {})
    assert len(result["items"]) == 1


def test_remember_fact_persists_as_fact_category(db_session, user_id):
    result = remember_fact(db_session, user_id, {"key": "cidade", "value": "São Paulo"})
    assert result["category"] == "fact"


def test_remember_preference_and_fact_with_same_key_do_not_collide(db_session, user_id):
    """key+category identifica a entrada — mesma key em categorias
    diferentes são registros distintos."""
    remember_preference(db_session, user_id, {"key": "estudo", "value": "à noite"})
    remember_fact(db_session, user_id, {"key": "estudo", "value": "faculdade de ADS"})

    items = get_memory(db_session, user_id, {})["items"]
    assert len(items) == 2


def test_forget_memory_requires_memory_id(db_session, user_id):
    with pytest.raises(ToolValidationError):
        forget_memory(db_session, user_id, {})


def test_forget_memory_removes_entry(db_session, user_id):
    entry = remember_fact(db_session, user_id, {"key": "cidade", "value": "São Paulo"})
    result = forget_memory(db_session, user_id, {"memory_id": entry["id"]})
    assert result == {"deleted": True, "memory_id": entry["id"]}
    assert get_memory(db_session, user_id, {})["items"] == []


def test_forget_memory_rejects_foreign_entry(db_session, user_id, other_user_id):
    foreign = remember_fact(db_session, other_user_id, {"key": "cidade", "value": "Rio"})
    with pytest.raises(ToolNotFoundError):
        forget_memory(db_session, user_id, {"memory_id": foreign["id"]})


def test_get_memory_filters_by_category(db_session, user_id):
    remember_preference(db_session, user_id, {"key": "horario_estudo", "value": "à noite"})
    remember_fact(db_session, user_id, {"key": "cidade", "value": "São Paulo"})

    result = get_memory(db_session, user_id, {"category": "fact"})
    assert [item["key"] for item in result["items"]] == ["cidade"]


def test_get_memory_rejects_invalid_category(db_session, user_id):
    with pytest.raises(ToolValidationError):
        get_memory(db_session, user_id, {"category": "not-a-real-category"})


def test_get_memory_filters_by_query_text(db_session, user_id):
    remember_fact(db_session, user_id, {"key": "cidade", "value": "São Paulo"})
    remember_fact(db_session, user_id, {"key": "curso", "value": "Análise e Desenvolvimento"})

    result = get_memory(db_session, user_id, {"query": "São Paulo"})
    assert [item["key"] for item in result["items"]] == ["cidade"]


def test_get_memory_only_returns_owner_entries(db_session, user_id, other_user_id):
    remember_fact(db_session, user_id, {"key": "cidade", "value": "São Paulo"})
    remember_fact(db_session, other_user_id, {"key": "cidade", "value": "Rio"})

    result = get_memory(db_session, user_id, {})
    assert len(result["items"]) == 1


def test_get_user_preferences_excludes_facts(db_session, user_id):
    remember_preference(db_session, user_id, {"key": "horario_estudo", "value": "à noite"})
    remember_fact(db_session, user_id, {"key": "cidade", "value": "São Paulo"})

    result = get_user_preferences(db_session, user_id, {})
    assert [item["key"] for item in result["items"]] == ["horario_estudo"]


# --- select_relevant_context (usado pelo Orquestrador, não é uma tool) -----


def test_select_relevant_context_always_includes_all_preferences(db_session, user_id):
    remember_preference(db_session, user_id, {"key": "horario_estudo", "value": "à noite"})
    context = select_relevant_context(db_session, user_id, "mensagem sem relação nenhuma")
    assert context.preferences == {"horario_estudo": "à noite"}


def test_select_relevant_context_filters_facts_by_keyword_overlap(db_session, user_id):
    remember_fact(db_session, user_id, {"key": "cidade", "value": "mora em São Paulo"})
    remember_fact(db_session, user_id, {"key": "curso", "value": "faculdade de Análise e Desenvolvimento"})

    context = select_relevant_context(db_session, user_id, "will eu ainda moro em São Paulo?")
    assert context.memory == ["cidade: mora em São Paulo"]


def test_select_relevant_context_caps_number_of_memory_entries(db_session, user_id):
    for i in range(10):
        remember_fact(db_session, user_id, {"key": f"fato{i}", "value": "futebol futebol futebol"})

    context = select_relevant_context(db_session, user_id, "gosto muito de futebol")
    assert len(context.memory) <= 5
