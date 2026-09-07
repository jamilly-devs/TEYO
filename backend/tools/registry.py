"""Registro central da camada de Tools — o único ponto por onde o
Orquestrador executa ações (ARCHITECTURE.md: 'o LLM nunca acessa o banco
diretamente')."""

from typing import Any

from sqlalchemy.orm import Session

from llm.base import ToolSpec
from tools import events, finance, goals, market, tasks
from tools.base import ToolDefinition
from tools.errors import UnknownToolError


class ToolRegistry:
    def __init__(self, definitions: list[ToolDefinition]):
        self._by_name = {definition.spec.name: definition for definition in definitions}

    def specs(self) -> list[ToolSpec]:
        return [definition.spec for definition in self._by_name.values()]

    def is_destructive(self, name: str) -> bool:
        definition = self._by_name.get(name)
        return definition.destructive if definition is not None else False

    def execute(
        self, db: Session, user_id: int, name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        definition = self._by_name.get(name)
        if definition is None:
            raise UnknownToolError(f"tool desconhecida: {name}")
        return definition.execute(db, user_id, arguments)


def default_tool_registry() -> ToolRegistry:
    return ToolRegistry(
        [
            *tasks.DEFINITIONS,
            *events.DEFINITIONS,
            *goals.DEFINITIONS,
            *market.DEFINITIONS,
            *finance.DEFINITIONS,
        ]
    )
