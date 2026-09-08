import json
from datetime import datetime, timedelta
from typing import Optional

import pytest

from api.main import app
from api.routers.conversation import get_llm_provider
from db.models.enums import TaskCategory, TaskStatus
from db.models.task import Task
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
        self.contexts: list[Context] = []

    def generate(
        self,
        system_prompt: str,
        context: Context,
        available_tools: list[ToolSpec],
        conversation: list[Message],
    ) -> LLMResponse:
        self.calls.append(list(conversation))
        self.contexts.append(context)
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


# --- FASE 6: memória chega e sai da conversa --------------------------------


def test_remember_preference_tool_call_persists_and_shows_up_in_later_context(
    authenticated_client,
):
    stub = StubLLMProvider(
        responses=[
            LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        name="remember_preference",
                        arguments={"key": "horario_estudo", "value": "à noite"},
                    )
                ],
            ),
            LLMResponse(content="Beleza, vou lembrar que você prefere estudar à noite."),
        ]
    )
    _override_llm(stub)
    try:
        response = authenticated_client.post(
            "/conversation/message", json={"content": "eu prefiro estudar à noite"}
        )
        assert response.status_code == 200
        assert "à noite" in response.json()["content"].lower()
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)

    # turno seguinte: o Context já deve trazer a preferência recém-salva
    stub2 = StubLLMProvider(response=LLMResponse(content="Beleza, combinado!"))
    _override_llm(stub2)
    try:
        authenticated_client.post("/conversation/message", json={"content": "beleza"})
        assert stub2.contexts[-1].preferences == {"horario_estudo": "à noite"}
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_forget_memory_tool_call_removes_it_from_later_context(authenticated_client):
    """Ponta a ponta só por HTTP/conversa (sem acessar o banco por fora):
    lembra um fato, descobre o memory_id consultando get_memory pela
    própria conversa, esquece, confirma que sumiu do contexto seguinte."""
    remember_stub = StubLLMProvider(
        responses=[
            LLMResponse(
                content="",
                tool_calls=[ToolCall(name="remember_fact", arguments={"key": "cidade", "value": "São Paulo"})],
            ),
            LLMResponse(content="Beleza, anotado que você mora em São Paulo."),
        ]
    )
    _override_llm(remember_stub)
    try:
        authenticated_client.post(
            "/conversation/message", json={"content": "eu moro em São Paulo"}
        )
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)

    lookup_stub = StubLLMProvider(
        responses=[
            LLMResponse(
                content="", tool_calls=[ToolCall(name="get_memory", arguments={"query": "São Paulo"})]
            ),
            LLMResponse(content="Achei aqui."),
        ]
    )
    _override_llm(lookup_stub)
    try:
        authenticated_client.post("/conversation/message", json={"content": "o que você sabe sobre mim?"})
        tool_result = json.loads(lookup_stub.calls[1][-1].content)
        memory_id = tool_result["data"]["items"][0]["id"]
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)

    forget_stub = StubLLMProvider(
        responses=[
            LLMResponse(
                content="", tool_calls=[ToolCall(name="forget_memory", arguments={"memory_id": memory_id})]
            ),
            LLMResponse(content="Prontinho, esqueci isso."),
        ]
    )
    _override_llm(forget_stub)
    try:
        response = authenticated_client.post(
            "/conversation/message", json={"content": "pode esquecer que eu moro em São Paulo"}
        )
        assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)

    final_stub = StubLLMProvider(response=LLMResponse(content="Ok!"))
    _override_llm(final_stub)
    try:
        authenticated_client.post("/conversation/message", json={"content": "beleza"})
        assert final_stub.contexts[-1].memory == []
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


# --- FASE 7: padrões chegam à conversa ---------------------------------------
#
# Cenário sintético igual ao de tests/integration/test_tools_patterns.py
# (mesma janela de referência, mesmos históricos), mas exercitado pelo
# caminho HTTP -> Orquestrador -> Adapter completo, não só pela tool
# isolada — auditoria da FASE 7 apontou que não havia nenhuma cobertura
# nesse nível (ao contrário da FASE 6, memória/preferências acima).

PATTERNS_NOW = datetime(2026, 9, 7, 12, 0, 0)


def _pattern_at(days_ago: int, hour: int) -> datetime:
    return (PATTERNS_NOW - timedelta(days=days_ago)).replace(
        hour=hour, minute=0, second=0, microsecond=0
    )


def _completed_pattern_task(db, user_id, category, when):
    task = Task(
        user_id=user_id, title="x", category=category, status=TaskStatus.DONE, updated_at=when
    )
    db.add(task)
    db.commit()
    return task


def _seed_active_house_pattern(db, user_id):
    for i in range(15):
        _completed_pattern_task(db, user_id, TaskCategory.HOUSE, _pattern_at(8 + (i % 14), 20))
    for offset in (20, 15, 10):
        _completed_pattern_task(db, user_id, TaskCategory.HOUSE, _pattern_at(offset, 8))


def _seed_deprecated_studies_pattern_with_recent_change(db, user_id):
    for i in range(24):
        _completed_pattern_task(db, user_id, TaskCategory.STUDIES, _pattern_at(8 + (i % 14), 20))
    for offset in (1, 2, 3, 4, 5, 6):
        _completed_pattern_task(db, user_id, TaskCategory.STUDIES, _pattern_at(offset, 8))
    _completed_pattern_task(db, user_id, TaskCategory.STUDIES, _pattern_at(7, 20))


def _patch_pattern_engine_now(monkeypatch):
    """Trava datetime.utcnow() do Motor de Padrões no mesmo instante de
    referência usado para gerar o histórico sintético acima (mesma técnica
    de test_tools_patterns.py:_patch_now — o Orquestrador chama
    select_relevant_patterns/refresh_patterns_for_user sem `now` explícito,
    igual às tools)."""
    import pattern_engine.task_time_of_day as engine

    class _FixedDatetime(datetime):
        @classmethod
        def utcnow(cls):
            return PATTERNS_NOW

    monkeypatch.setattr(engine, "datetime", _FixedDatetime)


def test_context_patterns_includes_active_pattern_and_recent_change_through_orchestrator(
    authenticated_client, client_db_session, monkeypatch
):
    """Context.patterns precisa ser calculado pelo Orquestrador a cada
    turno, antes da chamada ao LLM (orchestrator.py), e conter tanto o
    padrão ativo quanto a mudança recente detectada — não só quando a tool
    é chamada isoladamente."""
    _patch_pattern_engine_now(monkeypatch)
    user_id = authenticated_client.get("/auth/me").json()["id"]
    _seed_active_house_pattern(client_db_session, user_id)
    _seed_deprecated_studies_pattern_with_recent_change(client_db_session, user_id)

    stub = StubLLMProvider(response=LLMResponse(content="Oi!"))
    _override_llm(stub)
    try:
        response = authenticated_client.post("/conversation/message", json={"content": "oi"})
        assert response.status_code == 200

        patterns = stub.contexts[-1].patterns
        assert any("house" in line for line in patterns)
        assert any("Possível mudança" in line and "studies" in line for line in patterns)
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_get_patterns_empty_result_does_not_hide_a_detected_routine_change(
    authenticated_client, client_db_session, monkeypatch
):
    """Auditoria FASE 7: quando get_patterns é chamada para uma categoria
    recém-despromovida por divergência sustentada, o resultado vem com
    `items: []`, mas `routine_changes_detected: true` — e uma chamada
    seguinte a get_routine_changes devolve o detalhe real da mudança. Isso
    garante que o fluxo tem, em ambos os passos, o que precisa para nunca
    concluir "não há padrão/mudança" com a informação correta disponível
    (PATTERN_ENGINE.md, TOOLS.md)."""
    _patch_pattern_engine_now(monkeypatch)
    user_id = authenticated_client.get("/auth/me").json()["id"]
    _seed_deprecated_studies_pattern_with_recent_change(client_db_session, user_id)

    stub = StubLLMProvider(
        responses=[
            LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        name="get_patterns",
                        arguments={"pattern_type": "task_time_of_day:studies"},
                    )
                ],
            ),
            LLMResponse(content="", tool_calls=[ToolCall(name="get_routine_changes", arguments={})]),
            LLMResponse(content="Percebi que você mudou o horário de estudar pra manhã."),
        ]
    )
    _override_llm(stub)
    try:
        response = authenticated_client.post(
            "/conversation/message",
            json={"content": "você percebeu alguma mudança na minha rotina de estudos?"},
        )
        assert response.status_code == 200

        get_patterns_result = json.loads(stub.calls[1][-1].content)
        assert get_patterns_result["data"]["items"] == []
        assert get_patterns_result["data"]["routine_changes_detected"] is True

        get_routine_changes_result = json.loads(stub.calls[2][-1].content)
        changes = get_routine_changes_result["data"]["items"]
        assert len(changes) == 1
        assert changes[0]["category"] == "studies"
        assert changes[0]["recent_change"] is True
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
