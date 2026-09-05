from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models.enums import EventSource


class EventCreate(BaseModel):
    title: str
    start_at: datetime
    end_at: datetime
    source: Optional[EventSource] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_at: datetime
    end_at: datetime
    source: EventSource
    created_at: datetime
    updated_at: datetime
