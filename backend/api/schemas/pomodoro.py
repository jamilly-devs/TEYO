from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models.enums import PomodoroStatus


class PomodoroStartRequest(BaseModel):
    task_id: Optional[int] = None


class PomodoroSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: Optional[int]
    status: PomodoroStatus
    started_at: datetime
    ended_at: Optional[datetime]
