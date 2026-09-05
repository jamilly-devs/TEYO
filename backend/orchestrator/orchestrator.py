import logging
from datetime import datetime

from sqlalchemy.orm import Session

from db.models.conversation import Conversation
from db.models.conversation import Message as MessageModel
from db.models.enums import MessageRole
from llm.base import Context, LLMInvalidResponseError, LLMProvider, LLMUnavailableError, Message
from llm.config import CONVERSATION_HISTORY_WINDOW
from orchestrator.prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


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
    def __init__(self, llm: LLMProvider):
        self._llm = llm

    def handle_user_message(self, db: Session, user_id: int, text: str) -> MessageModel:
        conversation = get_or_create_conversation(db, user_id)

        user_message = MessageModel(
            conversation_id=conversation.id, role=MessageRole.USER, content=text
        )
        db.add(user_message)
        conversation.last_message_at = datetime.utcnow()
        db.commit()

        llm_conversation = self._recent_history(db, conversation.id)

        try:
            response = self._llm.generate(
                system_prompt=SYSTEM_PROMPT,
                context=Context(),
                available_tools=[],
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

        reply_text = response.content
        if response.tool_calls:
            # FASE 5 (Tools) ainda não existe: nenhuma tool é executável.
            # Mesmo tratamento de "ferramenta inexistente chamada pelo LLM"
            # de ERROR_HANDLING.md — não executa nada, não confirma ação.
            logger.warning(
                "tool_call recebido do LLM antes da FASE 5 existir: %s",
                [tc.name for tc in response.tool_calls],
            )
            reply_text = reply_text or (
                "Ainda não consigo realizar ações — só conversar por enquanto."
            )

        assistant_message = MessageModel(
            conversation_id=conversation.id, role=MessageRole.ASSISTANT, content=reply_text
        )
        db.add(assistant_message)
        conversation.last_message_at = datetime.utcnow()
        db.commit()
        db.refresh(assistant_message)

        return assistant_message

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
