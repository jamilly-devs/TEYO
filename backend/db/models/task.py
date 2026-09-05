from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from db.models.enums import TaskCategory, TaskPriority, TaskStatus, enum_values


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_user_id_status", "user_id", "status"),
        Index("ix_tasks_user_id_due_date", "user_id", "due_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False, create_constraint=True, values_callable=enum_values),
        nullable=False,
        server_default=TaskStatus.PENDING.value,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, native_enum=False, create_constraint=True, values_callable=enum_values),
        nullable=False,
        server_default=TaskPriority.MEDIUM.value,
    )
    category: Mapped[Optional[TaskCategory]] = mapped_column(
        Enum(TaskCategory, native_enum=False, create_constraint=True, values_callable=enum_values),
        nullable=True,
    )
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    pomodoro_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goals.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
