from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HabitCreate(BaseModel):
    title: str
    # DT-13/plano FASE 10: dias por semana, 1 a 7 (mesmo range do
    # CheckConstraint da tabela).
    frequency_target: int = Field(ge=1, le=7)


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    frequency_target: Optional[int] = Field(default=None, ge=1, le=7)


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    frequency_target: int
    created_at: datetime


class HabitWithStreakOut(HabitOut):
    streak: int


class HabitLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    completed_at: datetime
