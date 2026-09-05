from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from db.models.enums import MemoryCategory, MemorySource, enum_values


class MemoryEntry(Base):
    __tablename__ = "memory_entries"
    __table_args__ = (Index("ix_memory_entries_user_id_category", "user_id", "category"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[MemoryCategory] = mapped_column(
        Enum(
            MemoryCategory, native_enum=False, create_constraint=True, values_callable=enum_values
        ),
        nullable=False,
    )
    source: Mapped[MemorySource] = mapped_column(
        Enum(MemorySource, native_enum=False, create_constraint=True, values_callable=enum_values),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
