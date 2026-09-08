from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DailyPlanItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kind: str
    id: int
    title: str
    period: Optional[str]
    start_at: Optional[datetime]
    priority: Optional[str]
    reason: Optional[str]
    suggested_due_date: Optional[date]


class DailyPlanOut(BaseModel):
    date: date
    items: list[DailyPlanItemOut]


class ReorganizeRequest(BaseModel):
    energy_level: Optional[str] = None
