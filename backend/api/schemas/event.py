from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models.enums import EventSource


class EventCreate(BaseModel):
    title: str
    start_at: datetime
    end_at: datetime
    source: Optional[EventSource] = None
    confirm_overlap: Optional[bool] = None
    """FASE 8 (PLANNER.md/MODULES/AGENDA.md): só True depois que o usuário
    confirmar explicitamente que quer criar mesmo com sobreposição a outro
    compromisso — sem isso, um conflito não cria o evento (ver tools/events.py)."""


class EventUpdate(BaseModel):
    title: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    confirm_overlap: Optional[bool] = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_at: datetime
    end_at: datetime
    source: EventSource
    created_at: datetime
    updated_at: datetime
