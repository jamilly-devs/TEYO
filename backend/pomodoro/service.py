"""Serviço de Pomodoro (MODULES/POMODORO.md, FASE 10).

Usa EXCLUSIVAMENTE `pomodoro_sessions` (DT-8). Não escreve
`productivity_logs`. Estado controlado pelo sistema: `active` / `paused` /
`completed`. Só rastreia sessões de FOCO (DT-7); pausa é flip de status,
sem contabilização de tempo (DT-6). Uma sessão em andamento por usuário
(DT-5). A conclusão passa por `core.pomodoro_completion` (ponto único).

Não commita: quem originou a ação (router) é dono da transação — regra
FASE 8.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from db.models.enums import PomodoroStatus
from db.models.pomodoro import PomodoroSession
from db.models.task import Task


class PomodoroConflictError(Exception):
    """Já existe uma sessão em andamento (active/paused) — DT-5."""


class PomodoroNotFoundError(Exception):
    """Sessão (ou tarefa associada) não existe ou não pertence ao usuário."""


class PomodoroStateError(Exception):
    """Transição de estado inválida (ex.: retomar uma sessão não pausada)."""


def active_session(db: Session, user_id: int) -> Optional[PomodoroSession]:
    return (
        db.query(PomodoroSession)
        .filter(
            PomodoroSession.user_id == user_id,
            PomodoroSession.status.in_((PomodoroStatus.ACTIVE, PomodoroStatus.PAUSED)),
        )
        .first()
    )


def get_owned_session(db: Session, user_id: int, session_id: int) -> PomodoroSession:
    session = db.get(PomodoroSession, session_id)
    if session is None or session.user_id != user_id:
        raise PomodoroNotFoundError(f"sessão {session_id} não encontrada")
    return session


def start_session(
    db: Session,
    user_id: int,
    task_id: Optional[int] = None,
    now: Optional[datetime] = None,
) -> PomodoroSession:
    if active_session(db, user_id) is not None:
        raise PomodoroConflictError("já existe uma sessão de Pomodoro em andamento")
    if task_id is not None:
        task = db.get(Task, task_id)
        if task is None or task.user_id != user_id:
            raise PomodoroNotFoundError(f"tarefa {task_id} não encontrada")

    session = PomodoroSession(
        user_id=user_id,
        task_id=task_id,
        status=PomodoroStatus.ACTIVE,
        started_at=now or datetime.utcnow(),
    )
    db.add(session)
    db.flush()
    return session


def pause_session(db: Session, user_id: int, session_id: int) -> PomodoroSession:
    session = get_owned_session(db, user_id, session_id)
    if session.status != PomodoroStatus.ACTIVE:
        raise PomodoroStateError("só uma sessão ativa pode ser pausada")
    session.status = PomodoroStatus.PAUSED
    db.flush()
    return session


def resume_session(db: Session, user_id: int, session_id: int) -> PomodoroSession:
    session = get_owned_session(db, user_id, session_id)
    if session.status != PomodoroStatus.PAUSED:
        raise PomodoroStateError("só uma sessão pausada pode ser retomada")
    session.status = PomodoroStatus.ACTIVE
    db.flush()
    return session
