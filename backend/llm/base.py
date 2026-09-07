"""Fixed interface between the Orchestrator and the real model runtime
(LLM.md). Swapping models later means writing a new adapter that implements
`LLMProvider` — Orchestrator, Tools and the database never change.
"""

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant", "tool"]


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class Message:
    role: Role
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    """Preenchido só em mensagens `role="assistant"` que chamaram tools —
    permite reenviar ao Adapter, na rodada seguinte, o mesmo tool_call que o
    modelo fez, junto do resultado (`role="tool"`) que vem depois na
    conversa. Sem isso o modelo perde o contexto de qual chamada gerou qual
    resultado (LLM.md: normalização de tool calling)."""


@dataclass
class Context:
    """Memória relevante, padrões relevantes e preferências do usuário
    (LLM.md). FASE 4 não implementa Memória (FASE 6) nem Motor de Padrões
    (FASE 7) — os campos existem para não mudar a assinatura depois, mas
    ficam vazios por enquanto; não é uma decisão de produto, é só o
    contrato já vindo pronto para quando essas fases chegarem."""

    memory: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolSpec:
    """Espelha o contrato de uma tool de TOOLS.md: nome, descrição e
    parâmetros (JSON Schema)."""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMUnavailableError(Exception):
    """O runtime do LLM (Ollama) está indisponível ou não respondeu a
    tempo. Ver ERROR_HANDLING.md — nunca deve virar uma resposta fingindo
    sucesso."""


class LLMInvalidResponseError(Exception):
    """A resposta do modelo não seguiu o contrato de tool_call. O Adapter
    nunca tenta "adivinhar" o argumento faltante (LLM.md)."""


class LLMProvider:
    def generate(
        self,
        system_prompt: str,
        context: Context,
        available_tools: list[ToolSpec],
        conversation: list[Message],
    ) -> LLMResponse:
        raise NotImplementedError
