"""Streak INDIVIDUAL de um hábito (FASE 10, DT-1).

Semanas-calendário consecutivas (segunda–domingo, via `core.day_window`)
em que o hábito teve **>= `frequency_target`** logs. A semana corrente
conta como "em andamento": não soma enquanto não bate o alvo, mas também
não zera o streak. Um log isolado fora do padrão não quebra o hábito
(`MODULES/HABITS.md`).

É DISTINTO do streak global da gamificação (FASE 9) — este olha um hábito
só e conta semanas; aquele conta dias com qualquer atividade. A FASE 10
não altera o streak global.
"""

from collections import Counter
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from core.day_window import local_today
from db.models.habit import Habit, HabitLog
from db.models.user import User


def _week_start(day: date) -> date:
    """Segunda-feira da semana de `day`."""
    return day - timedelta(days=day.weekday())


def individual_streak(
    db: Session, habit_id: int, now: Optional[datetime] = None
) -> int:
    habit = db.get(Habit, habit_id)
    if habit is None:
        return 0
    user = db.get(User, habit.user_id)
    today = local_today(user, now=now) if user is not None else (
        now.date() if now is not None else datetime.utcnow().date()
    )

    rows = (
        db.query(HabitLog.completed_at)
        .filter(HabitLog.habit_id == habit_id)
        .all()
    )
    if not rows:
        return 0

    logs_per_week = Counter(_week_start(row[0].date()) for row in rows)
    target = habit.frequency_target

    streak = 0
    cursor = _week_start(today)
    if logs_per_week.get(cursor, 0) >= target:
        streak += 1
    cursor -= timedelta(days=7)
    while logs_per_week.get(cursor, 0) >= target:
        streak += 1
        cursor -= timedelta(days=7)
    return streak
