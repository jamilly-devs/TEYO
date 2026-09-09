"""habits/streak.py — streak individual (DT-1): semanas-calendário
consecutivas atingindo `frequency_target` logs; semana corrente em
andamento não zera; miss isolado não quebra."""

from datetime import datetime, timedelta

from db.models.habit import Habit, HabitLog
from habits.streak import individual_streak

# Terça-feira; semana de segunda 2026-09-07.
NOW = datetime(2026, 9, 9, 12, 0, 0)


def _habit(db, user_id, target=3) -> Habit:
    habit = Habit(user_id=user_id, title="ler", frequency_target=target)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def _log(db, habit, when) -> None:
    db.add(HabitLog(habit_id=habit.id, user_id=habit.user_id, completed_at=when))
    db.commit()


def test_no_logs_is_zero(db_session, user_id):
    habit = _habit(db_session, user_id)
    assert individual_streak(db_session, habit.id, now=NOW) == 0


def test_consecutive_weeks_meeting_target(db_session, user_id):
    habit = _habit(db_session, user_id, target=3)
    # semana atual (2026-09-07..): 3 logs -> conta
    for day in (7, 8, 9):
        _log(db_session, habit, datetime(2026, 9, day, 9, 0, 0))
    # semana anterior (2026-08-31..09-06): 3 logs -> conta
    for day in (1, 2, 3):
        _log(db_session, habit, datetime(2026, 9, day, 9, 0, 0))
    # duas semanas atrás (2026-08-24..): só 1 log -> quebra
    _log(db_session, habit, datetime(2026, 8, 25, 9, 0, 0))

    assert individual_streak(db_session, habit.id, now=NOW) == 2


def test_current_week_in_progress_does_not_reset(db_session, user_id):
    habit = _habit(db_session, user_id, target=3)
    # semana atual: só 1 log (ainda não bateu o alvo) -> não conta, não zera
    _log(db_session, habit, datetime(2026, 9, 9, 9, 0, 0))
    # semana anterior: 3 logs -> conta
    for day in (1, 2, 3):
        _log(db_session, habit, datetime(2026, 9, day, 9, 0, 0))

    assert individual_streak(db_session, habit.id, now=NOW) == 1


def test_isolated_miss_within_a_week_does_not_break(db_session, user_id):
    habit = _habit(db_session, user_id, target=2)
    # semana atual: 2 logs (bate alvo mesmo "faltando" dias) -> conta
    for day in (8, 9):
        _log(db_session, habit, datetime(2026, 9, day, 9, 0, 0))
    # semana anterior: 2 logs -> conta
    for day in (1, 4):
        _log(db_session, habit, datetime(2026, 9, day, 9, 0, 0))

    assert individual_streak(db_session, habit.id, now=NOW) == 2


def test_gap_week_breaks_streak(db_session, user_id):
    habit = _habit(db_session, user_id, target=2)
    for day in (8, 9):
        _log(db_session, habit, datetime(2026, 9, day, 9, 0, 0))
    # pula a semana anterior inteira; semana -2 tem 2 logs
    for day in (24, 25):
        _log(db_session, habit, datetime(2026, 8, day, 9, 0, 0))

    assert individual_streak(db_session, habit.id, now=NOW) == 1


def test_streak_is_per_habit(db_session, user_id):
    a = _habit(db_session, user_id, target=1)
    b = _habit(db_session, user_id, target=1)
    _log(db_session, a, datetime(2026, 9, 9, 9, 0, 0))

    assert individual_streak(db_session, a.id, now=NOW) == 1
    assert individual_streak(db_session, b.id, now=NOW) == 0
