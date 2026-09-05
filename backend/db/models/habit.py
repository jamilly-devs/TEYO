from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (
        Index("ix_habits_user_id", "user_id"),
        CheckConstraint(
            "frequency_target >= 1 AND frequency_target <= 7", name="ck_habits_frequency_target"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    frequency_target: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )


class HabitLog(Base):
    __tablename__ = "habit_logs"
    __table_args__ = (
        Index("ix_habit_logs_habit_id_completed_at", "habit_id", "completed_at"),
        Index("ix_habit_logs_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    context: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
