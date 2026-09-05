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

router = APIRouter(prefix="/events", tags=["events"])


def _get_owned_event(event_id: int, user: User, db: Session) -> Event:
    event = db.get(Event, event_id)
    if event is None or event.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")
    return event


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
    fields.setdefault("source", EventSource.MANUAL)
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
    for field, value in payload.model_dump(exclude_unset=True).items():
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
