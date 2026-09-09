"""Streak e métricas semanais da gamificação.

A definição de "dia"/fuso vem de `core.day_window` (a MESMA que o
Planejador usa) — nunca recalculada aqui (decisão FASE 8/FASE 9).

Limitação conhecida (mesma classe da do Motor de Padrões): os timestamps
em `gamification_events.created_at` são gravados em UTC ingênuo pelo
motor, enquanto "hoje" é resolvido no fuso do usuário; perto da meia-noite
pode haver deslocamento de um dia. `now` explícito (testes) é tratado como
já estando no fuso do usuário, igual a `core.day_window`.
"""

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from core.day_window import local_today
from db.models.enums import PomodoroStatus
from db.models.gamification import GamificationEvent
from db.models.pomodoro import PomodoroSession
from db.models.user import User
from gamification.config import STREAK_QUALIFYING_EVENTS


def _qualifying_days(db: Session, user_id: int) -> set[date]:
    rows = (
        db.query(GamificationEvent.created_at)
        .filter(
            GamificationEvent.user_id == user_id,
            GamificationEvent.event_type.in_(STREAK_QUALIFYING_EVENTS),
        )
        .all()
    )
    return {row[0].date() for row in rows}


def current_streak(db: Session, user_id: int, now: Optional[datetime] = None) -> int:
    """Nº de dias consecutivos, terminando hoje (ou ontem, se hoje ainda
    não teve atividade — um "hoje em aberto" não zera o streak), com pelo
    menos um evento qualificante."""
    user = db.get(User, user_id)
    if user is None:
        return 0
    today = local_today(user, now=now)
    days = _qualifying_days(db, user_id)
    if not days:
        return 0

    cursor = today if today in days else today - timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def weekly_pomodoro_hours(
    db: Session, user_id: int, now: Optional[datetime] = None
) -> float:
    """Horas somadas de sessões de Pomodoro concluídas na semana-calendário
    (segunda a domingo) do dia de hoje do usuário."""
    user = db.get(User, user_id)
    if user is None:
        return 0.0
    today = local_today(user, now=now)
    week_start = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())

    sessions = (
        db.query(PomodoroSession)
        .filter(
            PomodoroSession.user_id == user_id,
            PomodoroSession.status == PomodoroStatus.COMPLETED,
            PomodoroSession.started_at >= week_start,
            PomodoroSession.ended_at.isnot(None),
        )
        .all()
    )
    seconds = sum((s.ended_at - s.started_at).total_seconds() for s in sessions)
    return seconds / 3600.0
