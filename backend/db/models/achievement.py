from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Achievement(Base):
    """Conquista desbloqueada por um usuário (FASE 9).

    `DATABASE.md` (até a FASE 8) só previa `gamification_state` e
    `gamification_events`; esta tabela é acrescentada na FASE 9 para
    guardar o conjunto de conquistas já desbloqueadas de forma limpa
    (estado "desbloqueado atual", não só log). `code` referencia o
    catálogo em `gamification/config.py`. `UNIQUE(user_id, code)` garante
    que cada conquista desbloqueia uma única vez (idempotência do motor).
    """

    __tablename__ = "achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "code", name="uq_achievements_user_id_code"),
        Index("ix_achievements_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
