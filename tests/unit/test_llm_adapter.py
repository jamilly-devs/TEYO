import pytest

from llm.base import Context, LLMInvalidResponseError
from llm.ollama_adapter import OllamaAdapter


def test_parses_plain_text_response():
    data = {"message": {"role": "assistant", "content": "A capital do Brasil é Brasília."}}
    result = OllamaAdapter._parse_response(data)
    assert result.content == "A capital do Brasil é Brasília."
    assert result.tool_calls == []


def test_parses_a_valid_tool_call():
    data = {
        "message": {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "create_task",
                        "arguments": {"title": "Estudar inglês"},
                    }
                }
            ],
        }
    }
    result = OllamaAdapter._parse_response(data)
    assert result.tool_calls[0].name == "create_task"
    assert result.tool_calls[0].arguments == {"title": "Estudar inglês"}


@pytest.mark.parametrize(
    "data",
    [
        {"message": {"tool_calls": [{"function": {"name": "create_task"}}]}},
        {"message": {"tool_calls": [{"function": {"arguments": {"title": "x"}}}]}},
        {"message": {"tool_calls": [{"function": {"name": "x", "arguments": "not a dict"}}]}},
        {"no_message_key": True},
    ],
)
def test_rejects_malformed_tool_calls_instead_of_guessing(data):
    with pytest.raises(LLMInvalidResponseError):
        OllamaAdapter._parse_response(data)


def test_tool_spec_is_translated_to_ollama_function_format():
    from llm.base import ToolSpec

    spec = ToolSpec(
        name="create_task",
        description="Cria uma tarefa.",
        parameters={"type": "object", "properties": {"title": {"type": "string"}}},
    )
    translated = OllamaAdapter._tool_spec_to_ollama(spec)
    assert translated == {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Cria uma tarefa.",
            "parameters": spec.parameters,
        },
    }


def test_build_messages_replays_tool_calls_and_tool_results():
    """FASE 5: depois de executar uma tool, o Orquestrador reenvia a
    mensagem do assistente com `tool_calls` e o resultado (`role="tool"`)
    de volta ao modelo — o Adapter precisa serializar isso no mesmo
    formato que ele próprio leu em `_parse_response`."""
    from llm.base import Message, ToolCall

    conversation = [
        Message(role="user", content="cria uma tarefa de estudar inglês"),
        Message(
            role="assistant",
            content="",
            tool_calls=[ToolCall(name="create_task", arguments={"title": "Estudar inglês"})],
        ),
        Message(role="tool", content='{"status": "success", "data": {"id": 1}}'),
    ]

    messages = OllamaAdapter._build_messages("system prompt", Context(), conversation)

    assert messages[2] == {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {"function": {"name": "create_task", "arguments": {"title": "Estudar inglês"}}}
        ],
    }
    assert messages[3] == {
        "role": "tool",
        "content": '{"status": "success", "data": {"id": 1}}',
    }


def test_build_messages_omits_tool_calls_key_when_there_are_none():
    from llm.base import Message

    messages = OllamaAdapter._build_messages(
        "system prompt", Context(), [Message(role="user", content="oi")]
    )
    assert "tool_calls" not in messages[1]


def test_build_messages_has_no_context_system_message_when_context_is_empty():
    from llm.base import Message

    messages = OllamaAdapter._build_messages(
        "system prompt", Context(), [Message(role="user", content="oi")]
    )
    assert [m["role"] for m in messages] == ["system", "user"]


def test_build_messages_injects_preferences_and_memory_as_a_second_system_message():
    from llm.base import Message

    context = Context(memory=["cidade: São Paulo"], preferences={"horario_estudo": "à noite"})
    messages = OllamaAdapter._build_messages(
        "system prompt", context, [Message(role="user", content="oi")]
    )

    assert [m["role"] for m in messages] == ["system", "system", "user"]
    context_message = messages[1]["content"]
    assert "horario_estudo: à noite" in context_message
    assert "cidade: São Paulo" in context_message


def test_render_context_is_empty_string_when_nothing_to_report():
    assert OllamaAdapter._render_context(Context()) == ""
