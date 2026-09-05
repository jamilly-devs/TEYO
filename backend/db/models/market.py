from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from db.models.enums import MarketItemStatus, enum_values


class MarketItem(Base):
    __tablename__ = "market_items"
    __table_args__ = (Index("ix_market_items_user_id_status", "user_id", "status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_recurring_suggestion: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0"
    )
    status: Mapped[MarketItemStatus] = mapped_column(
        Enum(
            MarketItemStatus, native_enum=False, create_constraint=True, values_callable=enum_values
        ),
        nullable=False,
        server_default=MarketItemStatus.ACTIVE.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
