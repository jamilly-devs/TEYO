"""gamification/streak.py — dias consecutivos e horas semanais de Pomodoro,
com a definição de "dia" vinda de core.day_window (mesma do Planejador)."""

from datetime import datetime, timedelta

from db.models.enums import PomodoroStatus
from db.models.gamification import GamificationEvent
from db.models.pomodoro import PomodoroSession
from gamification.streak import current_streak, weekly_pomodoro_hours

NOW = datetime(2026, 9, 9, 12, 0, 0)  # terça-feira


def _event(db, user_id, day_offset, event_type="task_completed"):
    db.add(
        GamificationEvent(
            user_id=user_id,
            event_type=event_type,
            xp_delta=10,
            created_at=NOW - timedelta(days=day_offset),
        )
    )
    db.commit()


def test_streak_counts_consecutive_days_ending_today(db_session, user_id):
    for offset in (0, 1, 2):
        _event(db_session, user_id, offset)
    assert current_streak(db_session, user_id, now=NOW) == 3


def test_open_today_does_not_reset_streak(db_session, user_id):
    for offset in (1, 2):  # ontem e anteontem, nada hoje
        _event(db_session, user_id, offset)
    assert current_streak(db_session, user_id, now=NOW) == 2


def test_gap_breaks_streak(db_session, user_id):
    for offset in (0, 1, 3, 4):  # buraco no dia -2
        _event(db_session, user_id, offset)
    assert current_streak(db_session, user_id, now=NOW) == 2


def test_non_qualifying_events_do_not_feed_streak(db_session, user_id):
    _event(db_session, user_id, 0, event_type="achievement_unlocked")
    assert current_streak(db_session, user_id, now=NOW) == 0


def test_streak_isolated_by_user(db_session, user_id, other_user_id):
    _event(db_session, other_user_id, 0)
    assert current_streak(db_session, user_id, now=NOW) == 0


def test_weekly_pomodoro_hours_sums_only_this_week_completed(db_session, user_id):
    this_week = datetime(2026, 9, 8, 9, 0, 0)  # segunda desta semana
    db_session.add(
        PomodoroSession(
            user_id=user_id,
            status=PomodoroStatus.COMPLETED,
            started_at=this_week,
            ended_at=this_week + timedelta(hours=2),
        )
    )
    last_week = datetime(2026, 9, 1, 9, 0, 0)
    db_session.add(
        PomodoroSession(
            user_id=user_id,
            status=PomodoroStatus.COMPLETED,
            started_at=last_week,
            ended_at=last_week + timedelta(hours=5),
        )
    )
    db_session.commit()
    assert weekly_pomodoro_hours(db_session, user_id, now=NOW) == 2.0
