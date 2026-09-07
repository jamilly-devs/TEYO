import httpx

from llm.base import (
    Context,
    LLMInvalidResponseError,
    LLMProvider,
    LLMResponse,
    LLMUnavailableError,
    Message,
    ToolCall,
    ToolSpec,
)
from llm.config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_THINK, OLLAMA_TIMEOUT_SECONDS


class OllamaAdapter(LLMProvider):
    """Fala com um Ollama local servindo qwen3.5:4b via `POST /api/chat`.
    Normaliza a saída para o formato único de tool_call do Adapter (nome +
    argumentos tipados) — nunca tenta adivinhar um argumento ausente ou
    malformado (LLM.md)."""

    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL):
        self._host = host
        self._model = model

    def generate(
        self,
        system_prompt: str,
        context: Context,
        available_tools: list[ToolSpec],
        conversation: list[Message],
    ) -> LLMResponse:
        payload: dict = {
            "model": self._model,
            "messages": self._build_messages(system_prompt, context, conversation),
            "stream": False,
            "think": OLLAMA_THINK,
        }
        if available_tools:
            payload["tools"] = [self._tool_spec_to_ollama(tool) for tool in available_tools]

        try:
            response = httpx.post(
                f"{self._host}/api/chat", json=payload, timeout=OLLAMA_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise LLMUnavailableError(f"Ollama indisponível: {exc}") from exc

        return self._parse_response(data)

    @staticmethod
    def _build_messages(
        system_prompt: str, context: Context, conversation: list[Message]
    ) -> list[dict]:
        messages = [{"role": "system", "content": system_prompt}]
        context_text = OllamaAdapter._render_context(context)
        if context_text:
            # Mensagem de sistema separada, montada por turno (FASE 6: só
            # memória/preferências relevantes, nunca "a memória inteira" —
            # ver MEMORY.md e tools/memory.py:select_relevant_context).
            messages.append({"role": "system", "content": context_text})
        for m in conversation:
            entry: dict = {"role": m.role, "content": m.content}
            if m.tool_calls:
                # Mesmo formato que _parse_response lê de volta — replay
                # fiel do que o próprio Ollama mandou, para o modelo manter
                # o contexto de qual tool_call gerou qual resultado.
                entry["tool_calls"] = [
                    {"function": {"name": tc.name, "arguments": tc.arguments}}
                    for tc in m.tool_calls
                ]
            messages.append(entry)
        return messages

    @staticmethod
    def _render_context(context: Context) -> str:
        """Só preferências e memória (FASE 6). `context.patterns` fica sem
        uso até a FASE 7 definir o formato em PATTERN_ENGINE.md — nada
        aqui antecipa isso."""
        lines: list[str] = []
        if context.preferences:
            lines.append(
                "Preferências que o usuário já declarou "
                "(não invente novas, não repita como novidade):"
            )
            lines.extend(f"- {key}: {value}" for key, value in context.preferences.items())
        if context.memory:
            lines.append("Memória relevante a esta conversa:")
            lines.extend(f"- {item}" for item in context.memory)
        return "\n".join(lines)

    @staticmethod
    def _tool_spec_to_ollama(tool: ToolSpec) -> dict:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    @staticmethod
    def _parse_response(data: dict) -> LLMResponse:
        message = data.get("message")
        if not isinstance(message, dict):
            raise LLMInvalidResponseError(f"resposta sem `message` válida: {data!r}")

        content = message.get("content", "")
        raw_tool_calls = message.get("tool_calls") or []

        tool_calls = []
        for call in raw_tool_calls:
            function = call.get("function", {}) if isinstance(call, dict) else {}
            name = function.get("name")
            arguments = function.get("arguments")
            if not name or not isinstance(arguments, dict):
                raise LLMInvalidResponseError(f"tool_call malformado: {call!r}")
            tool_calls.append(ToolCall(name=name, arguments=arguments))

        return LLMResponse(content=content, tool_calls=tool_calls)
