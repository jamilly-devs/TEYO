"""Tools de Agenda (MODULES/AGENDA.md, TOOLS.md)."""

from datetime import datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.schemas.event import EventCreate, EventOut, EventUpdate
from db.models.enums import EventSource
from db.models.event import Event
from llm.base import ToolSpec
from planner.daily_plan import find_overlapping_events
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
    nunca interpreta linguagem natural de data/hora (TOOLS.md, MODULES/AGENDA.md).

    Sobreposição com um compromisso existente (MODULES/AGENDA.md,
    PLANNER.md — política confirmada com Jams na FASE 8): por padrão não
    cria e devolve `conflict: true` com os compromissos conflitantes, para
    o TEYO avisar e pedir confirmação — nunca bloqueia silenciosamente nem
    cria por conta própria. Só cria mesmo com sobreposição quando
    `confirm_overlap` vier `true` (usuário já confirmou explicitamente)."""
    try:
        payload = EventCreate(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    fields = payload.model_dump(exclude_unset=True)
    confirm_overlap = fields.pop("confirm_overlap", False)
    fields.setdefault("source", EventSource.TEYO_NLU)

    if not confirm_overlap:
        conflicts = find_overlapping_events(db, user_id, fields["start_at"], fields["end_at"])
        if conflicts:
            return {"conflict": True, "conflicting_events": [_serialize(e) for e in conflicts]}

    event = Event(user_id=user_id, **fields)
    db.add(event)
    db.commit()
    db.refresh(event)
    return _serialize(event)


def update_event(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    """Mesma política de sobreposição de `create_event` (ver acima) — só se
    aplica quando `start_at`/`end_at` estão sendo alterados; um `update_event`
    que só muda o título, por exemplo, não pode criar um conflito novo."""
    event_id = require_id(arguments, "event_id")
    event = _get_owned_event(db, user_id, event_id)

    rest = {key: value for key, value in arguments.items() if key != "event_id"}
    try:
        payload = EventUpdate(**rest)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    fields = payload.model_dump(exclude_unset=True)
    confirm_overlap = fields.pop("confirm_overlap", False)

    if not confirm_overlap and ("start_at" in fields or "end_at" in fields):
        new_start = fields.get("start_at", event.start_at)
        new_end = fields.get("end_at", event.end_at)
        conflicts = find_overlapping_events(
            db, user_id, new_start, new_end, exclude_event_id=event_id
        )
        if conflicts:
            return {"conflict": True, "conflicting_events": [_serialize(e) for e in conflicts]}

    for field, value in fields.items():
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
_CONFIRM_OVERLAP_FIELD = {
    "type": "boolean",
    "description": (
        "Só true depois que o usuário confirmar explicitamente, numa "
        "mensagem anterior, que quer criar/mover o compromisso mesmo com a "
        "sobreposição que você já avisou. Nunca comece uma chamada com "
        "true — só use depois de um `conflict: true` anterior e da "
        "confirmação do usuário."
    ),
}

DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="create_event",
            description=(
                "Cria um compromisso na agenda do usuário. Se sobrepor a um "
                "compromisso existente, não cria — devolve `conflict: true` "
                "com os compromissos conflitantes; avise o usuário e só "
                "chame de novo com confirm_overlap=true se ele confirmar "
                "que quer criar mesmo assim."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start_at": _DATETIME_FIELD,
                    "end_at": _DATETIME_FIELD,
                    "confirm_overlap": _CONFIRM_OVERLAP_FIELD,
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
                "identificar qual compromisso o usuário quer dizer. Se a "
                "mudança de horário sobrepor outro compromisso, não aplica — "
                "devolve `conflict: true`; só chame de novo com "
                "confirm_overlap=true depois da confirmação do usuário."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "event_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "start_at": _DATETIME_FIELD,
                    "end_at": _DATETIME_FIELD,
                    "confirm_overlap": _CONFIRM_OVERLAP_FIELD,
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
