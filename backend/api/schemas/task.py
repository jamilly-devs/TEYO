from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models.enums import TaskCategory, TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    category: Optional[TaskCategory] = None
    goal_id: Optional[int] = None
    pomodoro_enabled: Optional[bool] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    category: Optional[TaskCategory] = None
    is_recurring: Optional[bool] = None
    pomodoro_enabled: Optional[bool] = None
    goal_id: Optional[int] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    due_date: Optional[datetime]
    priority: TaskPriority
    category: Optional[TaskCategory]
    is_recurring: bool
    pomodoro_enabled: bool
    goal_id: Optional[int]
    created_at: datetime
    updated_at: datetime
