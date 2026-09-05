from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class GamificationState(Base):
    __tablename__ = "gamification_state"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    xp_total: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    level: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class GamificationEvent(Base):
    __tablename__ = "gamification_events"
    __table_args__ = (Index("ix_gamification_events_user_id_created_at", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    xp_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    related_entity_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    related_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
