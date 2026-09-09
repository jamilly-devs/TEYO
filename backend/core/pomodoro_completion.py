"""Ponto único de conclusão de sessão de Pomodoro (FASE 10), análogo a
`core.task_completion`.

Uma sessão "válida" (DT-4) dispara `core.domain_events.on_pomodoro_completed`
— a gamificação já está ligada a esse gancho desde a FASE 9, então o XP
não é duplicado e nenhuma regra de XP mora aqui. Idempotente: uma sessão
já `completed` não redispara. Não commita (quem chama é dono da
transação — regra FASE 8).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from core import domain_events
from db.models.enums import PomodoroStatus
from db.models.pomodoro import PomodoroSession

# DT-4: tempo mínimo decorrido para a sessão contar como válida e conceder
# XP. Evita "farm" com start+complete instantâneo. Ajustável aqui.
MIN_VALID_MINUTES = 1.0


def complete_session(
    db: Session,
    user_id: int,
    session: PomodoroSession,
    now: Optional[datetime] = None,
) -> bool:
    """Conclui a sessão. Devolve `True` se o gancho de domínio foi
    disparado (sessão válida), `False` caso contrário (já concluída ou
    curta demais)."""
    if session.status == PomodoroStatus.COMPLETED:
        return False

    session.status = PomodoroStatus.COMPLETED
    session.ended_at = now or datetime.utcnow()
    db.flush()

    elapsed_minutes = (session.ended_at - session.started_at).total_seconds() / 60.0
    if elapsed_minutes < MIN_VALID_MINUTES:
        return False

    domain_events.on_pomodoro_completed(db, user_id, session)
    return True
