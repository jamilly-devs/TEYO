"""Endpoints de Pomodoro (MODULES/POMODORO.md, FASE 10).

Sem tool de LLM (DT-9): timer é experiência de UI/tempo real. Persistência
só em `pomodoro_sessions` (DT-8). A conclusão passa pelo ponto único
`core.pomodoro_completion`, que dispara `on_pomodoro_completed` (a
gamificação já trata o XP desde a FASE 9 — sem duplicação aqui).
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.pomodoro import PomodoroSessionOut, PomodoroStartRequest
from core.pomodoro_completion import complete_session
from db.models.user import User
from db.session import get_db
from pomodoro import service
from pomodoro.service import (
    PomodoroConflictError,
    PomodoroNotFoundError,
    PomodoroStateError,
)

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


@router.post(
    "/sessions", response_model=PomodoroSessionOut, status_code=status.HTTP_201_CREATED
)
def start_session(
    payload: PomodoroStartRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session = service.start_session(db, user.id, payload.task_id)
    except PomodoroConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except PomodoroNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions/active", response_model=Optional[PomodoroSessionOut])
def get_active_session(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return service.active_session(db, user.id)


@router.post("/sessions/{session_id}/pause", response_model=PomodoroSessionOut)
def pause_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session = service.pause_session(db, user.id, session_id)
    except PomodoroNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PomodoroStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    db.commit()
    db.refresh(session)
    return session


@router.post("/sessions/{session_id}/resume", response_model=PomodoroSessionOut)
def resume_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session = service.resume_session(db, user.id, session_id)
    except PomodoroNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PomodoroStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    db.commit()
    db.refresh(session)
    return session


@router.post("/sessions/{session_id}/complete", response_model=PomodoroSessionOut)
def complete_pomodoro_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session = service.get_owned_session(db, user.id, session_id)
    except PomodoroNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    complete_session(db, user.id, session)
    db.commit()
    db.refresh(session)
    return session
