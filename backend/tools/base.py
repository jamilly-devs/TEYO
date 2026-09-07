"""Contrato comum de uma tool (TOOLS.md, ARCHITECTURE.md: 'todas as ações
que alteram ou consultam dados passam por tools com contrato definido')."""

from dataclasses import dataclass
from typing import Any, Callable

from sqlalchemy.orm import Session

from llm.base import ToolSpec

ToolFunction = Callable[[Session, int, dict[str, Any]], dict[str, Any]]


@dataclass
class ToolDefinition:
    spec: ToolSpec
    execute: ToolFunction
    destructive: bool = False
    """DECIDIDO (TOOLS.md, BUSINESS_RULES.md #4): ações destrutivas exigem
    confirmação explícita do usuário antes da chamada. A confirmação em si
    é conversacional (o LLM só chama a tool depois de o usuário confirmar
    na mensagem anterior) — este campo apenas marca a tool para reforço na
    descrição enviada ao LLM e para os testes de regressão da regra."""
