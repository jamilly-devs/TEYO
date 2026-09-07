"""Tools de Agenda (MODULES/AGENDA.md, TOOLS.md)."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.schemas.event import EventCreate, EventOut, EventUpdate
from db.models.enums import EventSource
from db.models.event import Event
from llm.base import ToolSpec
from tools.base import ToolDefinition
from tools.errors import ToolNotFoundError, ToolValidationError, format_validation_error, require_id


def _get_owned_event(db: Session, user_id: int, event_id: int) -> Event:
    event = db.get(Event, event_id)
    if event is None or event.user_id != user_id:
        raise ToolNotFoundError(f"compromisso {event_id} não encontrado")
    return event


def _serialize(event: Event) -> dict[str, Any]:
    return EventOut.model_validate(event).model_dump(mode="json")


def create_event(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    """`start_at`/`end_at` chegam já normalizados pelo Orquestrador — a tool
    nunca interpreta linguagem natural de data/hora (TOOLS.md, MODULES/AGENDA.md)."""
    try:
        payload = EventCreate(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    fields = payload.model_dump(exclude_unset=True)
    fields.setdefault("source", EventSource.TEYO_NLU)
    event = Event(user_id=user_id, **fields)
    db.add(event)
    db.commit()
    db.refresh(event)
    return _serialize(event)


def update_event(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    event_id = require_id(arguments, "event_id")
    event = _get_owned_event(db, user_id, event_id)

    rest = {key: value for key, value in arguments.items() if key != "event_id"}
    try:
        payload = EventUpdate(**rest)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return _serialize(event)


def delete_event(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    event_id = require_id(arguments, "event_id")
    event = _get_owned_event(db, user_id, event_id)
    db.delete(event)
    db.commit()
    return {"deleted": True, "event_id": event_id}


def list_events(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    events = db.query(Event).filter_by(user_id=user_id).all()
    return {"items": [_serialize(event) for event in events]}


_DATETIME_FIELD = {
    "type": "string",
    "format": "date-time",
    "description": "ISO 8601, já resolvido pelo Orquestrador — nunca texto livre.",
}

DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="create_event",
            description="Cria um compromisso na agenda do usuário.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start_at": _DATETIME_FIELD,
                    "end_at": _DATETIME_FIELD,
                },
                "required": ["title", "start_at", "end_at"],
            },
        ),
        execute=create_event,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="update_event",
            description=(
                "Atualiza campos de um compromisso existente. Requer event_id "
                "já resolvido sem ambiguidade — use list_events se precisar "
                "identificar qual compromisso o usuário quer dizer."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "event_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "start_at": _DATETIME_FIELD,
                    "end_at": _DATETIME_FIELD,
                },
                "required": ["event_id"],
            },
        ),
        execute=update_event,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="delete_event",
            description=(
                "Exclui um compromisso permanentemente. AÇÃO DESTRUTIVA: só "
                "chame depois que o usuário confirmar explicitamente, na "
                "conversa, que quer excluir este compromisso específico."
            ),
            parameters={
                "type": "object",
                "properties": {"event_id": {"type": "integer"}},
                "required": ["event_id"],
            },
        ),
        execute=delete_event,
        destructive=True,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="list_events",
            description=(
                "Lista os compromissos existentes do usuário. Use para "
                "consultar a agenda ou resolver a qual compromisso uma "
                "mensagem ambígua se refere antes de chamar update_event/"
                "delete_event."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=list_events,
    ),
]
