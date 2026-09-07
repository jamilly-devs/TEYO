"""Tools de Memória (MEMORY.md, TOOLS.md).

`remember_preference`, `remember_fact` e `forget_memory` não estavam na
lista-base de `TOOLS.md` (que só tinha `get_user_preferences`/`get_memory`,
leitura). Sem uma tool de escrita, `memory_entries` nunca seria criada a
partir da conversa — o que contradiz `MEMORY.md` ("quando algo é salvo: o
usuário declara uma preferência ou fato estável → vira `memory_entries`")
e `ACCEPTANCE_CRITERIA.md` (remoção de memória precisa funcionar). Decisão
tomada com Jams em 2026-09-06 (opção "tools de escrita conversacionais"),
registrada em `DOCUMENTATION_AUDIT.md`."""

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from db.models.enums import MemoryCategory, MemorySource
from db.models.memory import MemoryEntry
from llm.base import Context, ToolSpec
from tools.base import ToolDefinition
from tools.errors import ToolNotFoundError, ToolValidationError, format_validation_error, require_id

# MEMORY.md deixa "critério exato de relevância" A DEFINIR, sem OPÇÃO
# RECOMENDADA — escolha técnica desta fase: correspondência por palavra
# entre a mensagem atual e key/value de cada entrada não-preferência,
# limitada a um número pequeno de resultados para nunca mandar "a memória
# inteira" ao LLM (MEMORY.md: "não a memória inteira do usuário").
MAX_RELEVANT_MEMORY_ENTRIES = 5

# Preferências (BUSINESS_RULES.md, MEMORY.md) são poucas e devem moldar o
# comportamento do TEYO de forma consistente — por isso vão sempre
# inteiras para o Context, sem o filtro de relevância aplicado a fatos.


class _MemoryWrite(BaseModel):
    key: str
    value: str


def _tokenize(text: str) -> set[str]:
    return {word for word in re.findall(r"\w+", text.lower()) if len(word) >= 4}


def _serialize(entry: MemoryEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "key": entry.key,
        "value": entry.value,
        "category": entry.category.value,
        "source": entry.source.value,
        "updated_at": entry.updated_at.isoformat(),
    }


def _get_owned_entry(db: Session, user_id: int, memory_id: int) -> MemoryEntry:
    entry = db.get(MemoryEntry, memory_id)
    if entry is None or entry.user_id != user_id:
        raise ToolNotFoundError(f"entrada de memória {memory_id} não encontrada")
    return entry


def _upsert(
    db: Session, user_id: int, key: str, value: str, category: MemoryCategory
) -> dict[str, Any]:
    """DECIDIDO na implementação (MEMORY.md deixa 'versiona ou sobrescreve'
    A DEFINIR, sem recomendação): sobrescreve o registro existente — mesmo
    `key`+`category` do mesmo usuário é a mesma informação atualizada, não
    uma nova entrada. Não há versionamento de nenhuma outra entidade do V1;
    manter `memory_entries` consistente com isso."""
    entry = db.query(MemoryEntry).filter_by(user_id=user_id, key=key, category=category).first()
    if entry is None:
        entry = MemoryEntry(
            user_id=user_id,
            key=key,
            value=value,
            category=category,
            source=MemorySource.USER_STATED,
        )
        db.add(entry)
    else:
        entry.value = value
        entry.source = MemorySource.USER_STATED
        entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(entry)
    return _serialize(entry)


def remember_preference(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = _MemoryWrite(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc
    return _upsert(db, user_id, payload.key, payload.value, MemoryCategory.PREFERENCE)


def remember_fact(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = _MemoryWrite(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc
    return _upsert(db, user_id, payload.key, payload.value, MemoryCategory.FACT)


def forget_memory(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    memory_id = require_id(arguments, "memory_id")
    entry = _get_owned_entry(db, user_id, memory_id)
    db.delete(entry)
    db.commit()
    return {"deleted": True, "memory_id": memory_id}


def get_memory(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    query = db.query(MemoryEntry).filter_by(user_id=user_id)

    category = arguments.get("category")
    if category is not None:
        try:
            category_enum = MemoryCategory(category)
        except ValueError as exc:
            raise ToolValidationError(f"category inválida: {category!r}") from exc
        query = query.filter_by(category=category_enum)

    entries = query.all()

    search_text = arguments.get("query")
    if search_text:
        tokens = _tokenize(search_text)
        entries = [entry for entry in entries if tokens & _tokenize(f"{entry.key} {entry.value}")]

    return {"items": [_serialize(entry) for entry in entries]}


def get_user_preferences(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    entries = (
        db.query(MemoryEntry).filter_by(user_id=user_id, category=MemoryCategory.PREFERENCE).all()
    )
    return {"items": [_serialize(entry) for entry in entries]}


def select_relevant_context(db: Session, user_id: int, message_text: str) -> Context:
    """Chamada pelo Orquestrador antes de montar o prompt (MEMORY.md: 'O
    Orquestrador seleciona memória relevante ao turno atual... antes de
    montar o prompt para o LLM') — não é uma tool, o LLM nunca a chama
    diretamente."""
    preference_entries = (
        db.query(MemoryEntry).filter_by(user_id=user_id, category=MemoryCategory.PREFERENCE).all()
    )
    preferences = {entry.key: entry.value for entry in preference_entries}

    other_entries = (
        db.query(MemoryEntry)
        .filter(MemoryEntry.user_id == user_id, MemoryEntry.category != MemoryCategory.PREFERENCE)
        .all()
    )
    tokens = _tokenize(message_text)
    relevant = [
        entry for entry in other_entries if tokens & _tokenize(f"{entry.key} {entry.value}")
    ]
    memory = [f"{entry.key}: {entry.value}" for entry in relevant[:MAX_RELEVANT_MEMORY_ENTRIES]]

    return Context(memory=memory, preferences=preferences)


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="remember_preference",
            description=(
                "Guarda uma preferência estável que o usuário declarou "
                "explicitamente (ex.: 'eu prefiro estudar à noite'). NÃO use "
                "para estado emocional ou situacional pontual (ex.: 'hoje "
                "estou cansado') — isso não deve virar preferência "
                "permanente. Se já existir uma preferência com a mesma "
                "chave, o valor é atualizado."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": (
                            "Identificador curto e estável da preferência, "
                            "ex.: 'horario_estudo'."
                        ),
                    },
                    "value": {"type": "string", "description": "O que o usuário declarou."},
                },
                "required": ["key", "value"],
            },
        ),
        execute=remember_preference,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="remember_fact",
            description=(
                "Guarda um fato estável que o usuário declarou sobre si "
                "mesmo (ex.: 'moro em São Paulo'). NÃO use para estado "
                "emocional ou situacional pontual. Se já existir um fato "
                "com a mesma chave, o valor é atualizado."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Identificador curto e estável do fato, ex.: 'cidade'.",
                    },
                    "value": {"type": "string", "description": "O que o usuário declarou."},
                },
                "required": ["key", "value"],
            },
        ),
        execute=remember_fact,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="forget_memory",
            description=(
                "Remove uma entrada de memória (preferência ou fato) "
                "permanentemente. AÇÃO DESTRUTIVA: só chame depois que o "
                "usuário confirmar explicitamente, na conversa, que quer "
                "esquecer isso. Use get_memory ou get_user_preferences "
                "antes, se precisar descobrir o memory_id."
            ),
            parameters={
                "type": "object",
                "properties": {"memory_id": {"type": "integer"}},
                "required": ["memory_id"],
            },
        ),
        execute=forget_memory,
        destructive=True,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="get_memory",
            description=(
                "Consulta memória do usuário (preferências e fatos "
                "declarados), opcionalmente filtrando por texto (query) ou "
                "categoria. Use para descobrir o memory_id antes de "
                "remover, ou para checar o que já foi declarado antes de "
                "perguntar de novo."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Texto livre para filtrar por relevância.",
                    },
                    "category": {"type": "string", "enum": [c.value for c in MemoryCategory]},
                },
            },
        ),
        execute=get_memory,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="get_user_preferences",
            description="Lista todas as preferências que o usuário já declarou.",
            parameters={"type": "object", "properties": {}},
        ),
        execute=get_user_preferences,
    ),
]
