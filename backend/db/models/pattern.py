from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from db.models.enums import PatternStatus, enum_values


class Pattern(Base):
    __tablename__ = "patterns"
    __table_args__ = (
        Index("ix_patterns_user_id_status", "user_id", "status"),
        Index("ix_patterns_user_id_pattern_type", "user_id", "pattern_type"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_patterns_confidence"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    pattern_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[PatternStatus] = mapped_column(
        Enum(
            PatternStatus, native_enum=False, create_constraint=True, values_callable=enum_values
        ),
        nullable=False,
    )
    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class PatternEvent(Base):
    __tablename__ = "pattern_events"
    __table_args__ = (Index("ix_pattern_events_user_id_occurred_at", "user_id", "occurred_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    metadata_: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata", JSON, nullable=True
    )
