import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from db.models.conversation import Conversation
from db.models.conversation import Message as MessageModel
from db.models.enums import MessageRole
from llm.base import (
    Context,
    LLMInvalidResponseError,
    LLMProvider,
    LLMUnavailableError,
    Message,
    ToolCall,
)
from llm.config import CONVERSATION_HISTORY_WINDOW
from orchestrator.prompt import SYSTEM_PROMPT
from tools.errors import ToolError
from tools.registry import ToolRegistry, default_tool_registry

logger = logging.getLogger(__name__)

# Segurança técnica contra encadeamento infinito de tool_calls — nenhum
# documento define um limite (LLM.md não cobre esse caso), então é uma
# escolha de implementação, não de produto: generosa o bastante para
# qualquer fluxo real de FLOWS.md (nenhum deles encadeia mais de duas ou
# três ações), curta o bastante para nunca deixar uma resposta pendurada.
MAX_TOOL_ROUNDS = 4


class OrchestratorError(Exception):
    """Erro de conversa que deve virar uma resposta de erro explícita ao
    usuário — nunca uma resposta fingindo sucesso (ERROR_HANDLING.md)."""


def get_or_create_conversation(db: Session, user_id: int) -> Conversation:
    """Uma única conversa principal por usuário (BUSINESS_RULES.md #20) —
    garantido aqui, na aplicação, e não por constraint de banco (ver
    decisão registrada em db/models/conversation.py na FASE 1)."""
    conversation = (
        db.query(Conversation)
        .filter_by(user_id=user_id)
        .order_by(Conversation.started_at.asc())
        .first()
    )
    if conversation is None:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return conversation


class Orchestrator:
    def __init__(self, llm: LLMProvider, tools: Optional[ToolRegistry] = None):
        self._llm = llm
        self._tools = tools or default_tool_registry()

    def handle_user_message(self, db: Session, user_id: int, text: str) -> MessageModel:
        conversation = get_or_create_conversation(db, user_id)

        user_message = MessageModel(
            conversation_id=conversation.id, role=MessageRole.USER, content=text
        )
        db.add(user_message)
        conversation.last_message_at = datetime.utcnow()
        db.commit()

        llm_conversation = self._recent_history(db, conversation.id)
        available_tools = self._tools.specs()
        executed_tool_calls: list[dict] = []

        reply_text = ""
        for _ in range(MAX_TOOL_ROUNDS):
            try:
                response = self._llm.generate(
                    system_prompt=SYSTEM_PROMPT,
                    context=Context(),
                    available_tools=available_tools,
                    conversation=llm_conversation,
                )
            except LLMUnavailableError as exc:
                raise OrchestratorError(
                    "Não consegui falar com o TEYO agora. Tenta de novo em instantes."
                ) from exc
            except LLMInvalidResponseError as exc:
                raise OrchestratorError(
                    "O TEYO deu uma resposta que eu não consegui entender. Tenta de novo."
                ) from exc

            if not response.tool_calls:
                reply_text = response.content
                break

            llm_conversation.append(
                Message(role="assistant", content=response.content, tool_calls=response.tool_calls)
            )
            for call in response.tool_calls:
                result = self._run_tool(db, user_id, call)
                executed_tool_calls.append(
                    {"name": call.name, "arguments": call.arguments, "result": result}
                )
                llm_conversation.append(
                    Message(role="tool", content=json.dumps(result, default=str))
                )
        else:
            logger.warning(
                "conversa excedeu MAX_TOOL_ROUNDS=%s de tool_calls para user_id=%s",
                MAX_TOOL_ROUNDS,
                user_id,
            )
            reply_text = (
                "Não consegui terminar essa ação — foram muitos passos. "
                "Pode tentar de novo ou me contar de outro jeito o que você quer?"
            )

        assistant_message = MessageModel(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=reply_text,
            tool_calls=executed_tool_calls or None,
        )
        db.add(assistant_message)
        conversation.last_message_at = datetime.utcnow()
        db.commit()
        db.refresh(assistant_message)

        return assistant_message

    def _run_tool(self, db: Session, user_id: int, call: ToolCall) -> dict:
        """Executa uma tool e devolve um resultado explícito de
        sucesso/erro — nunca deixa uma exceção de tool virar uma resposta
        de sucesso fingido (ERROR_HANDLING.md: 'Tool falha → Orquestrador
        recebe erro da tool, repassa ao LLM como resultado de erro')."""
        try:
            data = self._tools.execute(db, user_id, call.name, call.arguments)
            return {"status": "success", "data": data}
        except ToolError as exc:
            db.rollback()
            logger.warning("tool '%s' falhou para user_id=%s: %s", call.name, user_id, exc)
            return {"status": "error", "message": str(exc)}

    @staticmethod
    def _recent_history(db: Session, conversation_id: int) -> list[Message]:
        rows = (
            db.query(MessageModel)
            .filter_by(conversation_id=conversation_id)
            .order_by(MessageModel.created_at.desc())
            .limit(CONVERSATION_HISTORY_WINDOW)
            .all()
        )
        rows.reverse()
        return [Message(role=row.role.value, content=row.content) for row in rows]
