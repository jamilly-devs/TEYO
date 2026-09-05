import pytest

from llm.base import LLMInvalidResponseError
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
