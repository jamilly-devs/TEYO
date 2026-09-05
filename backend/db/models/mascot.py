from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class MascotState(Base):
    """Evolution stage and expression catalogs are still A DEFINIR (FASE 9);
    `evolution_stage` is a bare ordinal placeholder and `current_expression`
    intentionally has no default value or fixed vocabulary yet."""

    __tablename__ = "mascot_state"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    evolution_stage: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    current_expression: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
