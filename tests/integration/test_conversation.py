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
    """Permite programar uma resposta única (repetida em toda chamada) ou
    uma sequência de respostas — necessário na FASE 5 porque um tool_call
    dispara uma segunda chamada a `generate()` com o resultado da tool já
    no histórico, antes da resposta final em linguagem natural."""

    def __init__(
        self,
        response: Optional[LLMResponse] = None,
        responses: Optional[list[LLMResponse]] = None,
        error: Optional[Exception] = None,
    ):
        if responses is not None:
            self.responses = list(responses)
        elif response is not None:
            self.responses = [response]
        else:
            self.responses = []
        self.error = error
        self.calls: list[list[Message]] = []

    def generate(
        self,
        system_prompt: str,
        context: Context,
        available_tools: list[ToolSpec],
        conversation: list[Message],
    ) -> LLMResponse:
        self.calls.append(list(conversation))
        if self.error is not None:
            raise self.error
        if not self.responses:
            raise AssertionError("StubLLMProvider ficou sem respostas programadas")
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


@pytest.fixture()
def stub_llm():
    stub = StubLLMProvider(response=LLMResponse(content="Oi! Tudo certo por aqui."))
    app.dependency_overrides[get_llm_provider] = lambda: stub
    yield stub
    app.dependency_overrides.pop(get_llm_provider, None)


def _override_llm(stub: StubLLMProvider):
    app.dependency_overrides[get_llm_provider] = lambda: stub


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
    assert [m["content"] for m in history] == [
        "primeira",
        "Oi! Tudo certo por aqui.",
        "segunda",
        "Oi! Tudo certo por aqui.",
    ]


def test_llm_unavailable_returns_503_and_does_not_fake_success(authenticated_client):
    stub = StubLLMProvider(error=LLMUnavailableError("Ollama fora do ar"))
    _override_llm(stub)
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
    _override_llm(stub)
    try:
        response = authenticated_client.post("/conversation/message", json={"content": "oi"})
        assert response.status_code == 503
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_empty_message_is_rejected(authenticated_client, stub_llm):
    response = authenticated_client.post("/conversation/message", json={"content": ""})
    assert response.status_code == 422


# --- FASE 5: execução real de tools a partir da conversa -------------------


def test_tool_call_creates_task_and_confirms_success_in_final_reply(authenticated_client):
    stub = StubLLMProvider(
        responses=[
            LLMResponse(
                content="",
                tool_calls=[ToolCall(name="create_task", arguments={"title": "Estudar inglês"})],
            ),
            LLMResponse(content="Beleza, criei a tarefa 'Estudar inglês' pra você."),
        ]
    )
    _override_llm(stub)
    try:
        response = authenticated_client.post(
            "/conversation/message", json={"content": "cria uma tarefa de estudar inglês"}
        )
        assert response.status_code == 200
        assert "criei" in response.json()["content"].lower()

        tasks = authenticated_client.get("/tasks").json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Estudar inglês"

        # a segunda chamada ao LLM já recebeu o resultado da tool no
        # histórico, como mensagem role="tool" com status de sucesso
        second_call_messages = stub.calls[1]
        tool_result_message = second_call_messages[-1]
        assert tool_result_message.role == "tool"
        assert '"status": "success"' in tool_result_message.content
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_destructive_tool_call_executes_when_llm_calls_it(authenticated_client):
    """A confirmação em si é conversacional (o TEYO só chama a tool depois
    de o usuário confirmar, ver system prompt) — aqui testamos que, uma vez
    chamada, a tool destrutiva realmente executa e o resultado chega ao
    banco (BUSINESS_RULES.md #4)."""
    task = authenticated_client.post("/tasks", json={"title": "cancelar academia"}).json()

    stub = StubLLMProvider(
        responses=[
            LLMResponse(
                content="", tool_calls=[ToolCall(name="delete_task", arguments={"task_id": task["id"]})]
            ),
            LLMResponse(content="Prontinho, excluí a tarefa."),
        ]
    )
    _override_llm(stub)
    try:
        response = authenticated_client.post(
            "/conversation/message", json={"content": "sim, pode excluir"}
        )
        assert response.status_code == 200
        assert authenticated_client.get("/tasks").json() == []
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_tool_call_with_missing_required_param_does_not_execute_anything(authenticated_client):
    stub = StubLLMProvider(
        responses=[
            LLMResponse(content="", tool_calls=[ToolCall(name="create_task", arguments={})]),
            LLMResponse(content="Preciso saber o título da tarefa."),
        ]
    )
    _override_llm(stub)
    try:
        response = authenticated_client.post(
            "/conversation/message", json={"content": "cria uma tarefa"}
        )
        assert response.status_code == 200
        assert authenticated_client.get("/tasks").json() == []

        # o erro de validação foi repassado ao LLM como falha, não sucesso
        second_call_messages = stub.calls[1]
        tool_result_message = second_call_messages[-1]
        assert tool_result_message.role == "tool"
        assert '"status": "error"' in tool_result_message.content
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_unknown_tool_call_is_rejected_without_executing_anything(authenticated_client):
    stub = StubLLMProvider(
        responses=[
            LLMResponse(content="", tool_calls=[ToolCall(name="delete_everything", arguments={})]),
            LLMResponse(content="Desculpa, não consegui fazer isso."),
        ]
    )
    _override_llm(stub)
    try:
        response = authenticated_client.post(
            "/conversation/message", json={"content": "apaga tudo"}
        )
        assert response.status_code == 200
        assert "não confirmou nada" not in response.json()["content"].lower()
        assert authenticated_client.get("/tasks").json() == []
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_tool_call_loop_has_a_hard_limit_and_never_fakes_success(authenticated_client):
    """Se o modelo continuar encadeando tool_calls indefinidamente, o
    Orquestrador para depois de MAX_TOOL_ROUNDS e informa a falha — nunca
    trava a requisição nem finge que terminou com sucesso."""
    stub = StubLLMProvider(
        response=LLMResponse(
            content="", tool_calls=[ToolCall(name="list_tasks", arguments={})]
        )
    )
    _override_llm(stub)
    try:
        response = authenticated_client.post(
            "/conversation/message", json={"content": "lista minhas tarefas"}
        )
        assert response.status_code == 200
        body = response.json()["content"].lower()
        assert "criei" not in body
        assert "concluí" not in body
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
