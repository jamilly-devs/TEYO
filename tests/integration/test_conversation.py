from typing import Optional

import pytest

from api.main import app
from api.routers.conversation import get_llm_provider
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


class StubLLMProvider(LLMProvider):
    def __init__(
        self, response: Optional[LLMResponse] = None, error: Optional[Exception] = None
    ):
        self.response = response
        self.error = error
        self.calls: list[list[Message]] = []

    def generate(
        self,
        system_prompt: str,
        context: Context,
        available_tools: list[ToolSpec],
        conversation: list[Message],
    ) -> LLMResponse:
        self.calls.append(conversation)
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture()
def stub_llm():
    stub = StubLLMProvider(response=LLMResponse(content="Oi! Tudo certo por aqui."))
    app.dependency_overrides[get_llm_provider] = lambda: stub
    yield stub
    app.dependency_overrides.pop(get_llm_provider, None)


def test_send_message_persists_user_and_assistant_messages(authenticated_client, stub_llm):
    response = authenticated_client.post("/conversation/message", json={"content": "oi"})
    assert response.status_code == 200
    assert response.json()["role"] == "assistant"
    assert response.json()["content"] == "Oi! Tudo certo por aqui."

    history = authenticated_client.get("/conversation/history").json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[0]["content"] == "oi"


def test_reuses_the_single_main_conversation_across_messages(authenticated_client, stub_llm):
    authenticated_client.post("/conversation/message", json={"content": "primeira"})
    authenticated_client.post("/conversation/message", json={"content": "segunda"})

    history = authenticated_client.get("/conversation/history").json()
    assert [m["content"] for m in history] == ["primeira", "Oi! Tudo certo por aqui.", "segunda", "Oi! Tudo certo por aqui."]


def test_llm_unavailable_returns_503_and_does_not_fake_success(authenticated_client):
    stub = StubLLMProvider(error=LLMUnavailableError("Ollama fora do ar"))
    app.dependency_overrides[get_llm_provider] = lambda: stub
    try:
        response = authenticated_client.post("/conversation/message", json={"content": "oi"})
        assert response.status_code == 503

        history = authenticated_client.get("/conversation/history").json()
        # a mensagem do usuário foi salva, mas nenhuma resposta de
        # assistente falsa foi criada
        assert [m["role"] for m in history] == ["user"]
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_invalid_llm_response_returns_503(authenticated_client):
    stub = StubLLMProvider(error=LLMInvalidResponseError("JSON malformado"))
    app.dependency_overrides[get_llm_provider] = lambda: stub
    try:
        response = authenticated_client.post("/conversation/message", json={"content": "oi"})
        assert response.status_code == 503
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_attempted_tool_call_is_rejected_before_tools_exist(authenticated_client):
    stub = StubLLMProvider(
        response=LLMResponse(content="", tool_calls=[ToolCall(name="create_task", arguments={"title": "x"})])
    )
    app.dependency_overrides[get_llm_provider] = lambda: stub
    try:
        response = authenticated_client.post("/conversation/message", json={"content": "cria uma tarefa"})
        assert response.status_code == 200
        body = response.json()
        # nenhuma ação é confirmada ao usuário
        assert "criei" not in body["content"].lower()
        assert "concluí" not in body["content"].lower()
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_empty_message_is_rejected(authenticated_client, stub_llm):
    response = authenticated_client.post("/conversation/message", json={"content": ""})
    assert response.status_code == 422
