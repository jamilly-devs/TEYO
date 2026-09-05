from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models.enums import GoalStatus


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[date] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    target_date: Optional[date] = None


class GoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: GoalStatus
    target_date: Optional[date]
    created_at: datetime
    updated_at: datetime
