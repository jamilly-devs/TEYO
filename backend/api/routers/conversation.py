from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.conversation import MessageCreate, MessageOut
from db.models.conversation import Message as MessageModel
from db.models.user import User
from db.session import get_db
from llm.base import LLMProvider
from llm.ollama_adapter import OllamaAdapter
from orchestrator.orchestrator import Orchestrator, OrchestratorError, get_or_create_conversation

router = APIRouter(prefix="/conversation", tags=["conversation"])


def get_llm_provider() -> LLMProvider:
    return OllamaAdapter()


def get_orchestrator(llm: LLMProvider = Depends(get_llm_provider)) -> Orchestrator:
    return Orchestrator(llm)


@router.post("/message", response_model=MessageOut)
def send_message(
    payload: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> MessageModel:
    try:
        return orchestrator.handle_user_message(db, user.id, payload.content)
    except OrchestratorError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc


@router.get("/history", response_model=list[MessageOut])
def get_history(
    limit: int = Query(default=50, ge=1, le=200),
    before_id: Optional[int] = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageModel]:
    conversation = get_or_create_conversation(db, user.id)
    query = db.query(MessageModel).filter_by(conversation_id=conversation.id)
    if before_id is not None:
        query = query.filter(MessageModel.id < before_id)
    messages = query.order_by(MessageModel.id.desc()).limit(limit).all()
    messages.reverse()
    return messages
