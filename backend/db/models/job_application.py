from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from db.models.enums import JobApplicationStatus, enum_values


class JobApplication(Base):
    """Candidatura acompanhada manualmente pelo usuário (MODULES/CAREER.md,
    FASE 10).

    V1 = acompanhamento manual: sem busca automatizada de vagas, sem uso de
    LLM para buscar. `applied_on` é a data da candidatura (DT-10 do plano da
    FASE 10). Estrutura espelha `goal.py`.
    """

    __tablename__ = "job_applications"
    __table_args__ = (Index("ix_job_applications_user_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    applied_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[JobApplicationStatus] = mapped_column(
        Enum(
            JobApplicationStatus,
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
        server_default=JobApplicationStatus.INTERESTED.value,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
