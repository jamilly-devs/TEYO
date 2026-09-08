from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.event import EventCreate, EventOut, EventUpdate
from db.models.enums import EventSource
from db.models.event import Event
from db.models.user import User
from db.session import get_db
from planner.daily_plan import find_overlapping_events

router = APIRouter(prefix="/events", tags=["events"])


def _get_owned_event(event_id: int, user: User, db: Session) -> Event:
    event = db.get(Event, event_id)
    if event is None or event.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")
    return event


def _raise_conflict(conflicts: list[Event]) -> None:
    """FASE 8 (MODULES/AGENDA.md, PLANNER.md): sobreposição sinalizada com
    409, nunca criada/aplicada silenciosamente. O cliente confirma
    reenviando o mesmo payload com `confirm_overlap: true`."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "message": "compromisso sobreposto a outro já existente",
            "conflicting_events": [
                EventOut.model_validate(event).model_dump(mode="json") for event in conflicts
            ],
        },
    )


@router.get("", response_model=List[EventOut])
def list_events(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[Event]:
    return db.query(Event).filter_by(user_id=user.id).all()


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Event:
    fields = payload.model_dump(exclude_unset=True)
    confirm_overlap = fields.pop("confirm_overlap", False)
    fields.setdefault("source", EventSource.MANUAL)

    if not confirm_overlap:
        conflicts = find_overlapping_events(db, user.id, fields["start_at"], fields["end_at"])
        if conflicts:
            _raise_conflict(conflicts)

    event = Event(user_id=user.id, **fields)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Event:
    event = _get_owned_event(event_id, user, db)
    fields = payload.model_dump(exclude_unset=True)
    confirm_overlap = fields.pop("confirm_overlap", False)

    if not confirm_overlap and ("start_at" in fields or "end_at" in fields):
        new_start = fields.get("start_at", event.start_at)
        new_end = fields.get("end_at", event.end_at)
        conflicts = find_overlapping_events(
            db, user.id, new_start, new_end, exclude_event_id=event_id
        )
        if conflicts:
            _raise_conflict(conflicts)

    for field, value in fields.items():
        setattr(event, field, value)
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    event = _get_owned_event(event_id, user, db)
    db.delete(event)
    db.commit()
