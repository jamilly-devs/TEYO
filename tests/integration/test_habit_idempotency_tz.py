"""DT-2 — `log_habit` idempotente por DIA LOCAL do usuário, mesmo quando a
hora UTC já virou o dia.

Cenário de fronteira: 22:30 em São Paulo (UTC-3) == 01:30 UTC do dia
seguinte. Antes do fix, `completed_at` (UTC) caía no dia local seguinte e
a 2ª chamada do mesmo dia não era detectada como duplicada — farm de XP e
testes de idempotência sensíveis ao relógio."""

from datetime import datetime
from zoneinfo import ZoneInfo

import habits.service as habit_service
from db.models.gamification import GamificationEvent, GamificationState
from db.models.habit import Habit, HabitLog
from gamification import config

# 2026-09-09 22:30 em São Paulo  ==  2026-09-10 01:30 UTC (quarta vira terça-noite).
_INSTANT_UTC = datetime(2026, 9, 10, 1, 30, tzinfo=ZoneInfo("UTC"))
_LOCAL_DATE = _INSTANT_UTC.astimezone(ZoneInfo("America/Sao_Paulo")).date()  # 2026-09-09


def _freeze_sp_evening(monkeypatch):
    class _Frozen(datetime):
        @classmethod
        def now(cls, tz=None):
            if tz is not None:
                return _INSTANT_UTC.astimezone(tz)
            return _INSTANT_UTC.replace(tzinfo=None)

    monkeypatch.setattr(habit_service, "datetime", _Frozen)


def _habit(db, user_id) -> Habit:
    habit = Habit(user_id=user_id, title="ler", frequency_target=3)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def test_second_log_in_sp_evening_is_idempotent(db_session, user_id, monkeypatch):
    _freeze_sp_evening(monkeypatch)
    habit = _habit(db_session, user_id)

    first = habit_service.log_habit(db_session, user_id, habit)
    second = habit_service.log_habit(db_session, user_id, habit)
    db_session.commit()

    assert first["created"] is True
    assert second["created"] is False
    assert first["log"].id == second["log"].id
    assert db_session.query(HabitLog).filter_by(habit_id=habit.id).count() == 1


def test_evening_log_is_stamped_on_the_local_day(db_session, user_id, monkeypatch):
    _freeze_sp_evening(monkeypatch)
    habit = _habit(db_session, user_id)

    result = habit_service.log_habit(db_session, user_id, habit)
    db_session.commit()

    # dia LOCAL (2026-09-09), não o dia UTC (2026-09-10)
    assert result["log"].completed_at.date() == _LOCAL_DATE
    assert result["log"].context == {
        "hour": 22,
        "weekday": datetime(2026, 9, 9).weekday(),
    }


def test_evening_double_log_does_not_double_xp(db_session, user_id, monkeypatch):
    _freeze_sp_evening(monkeypatch)
    habit = _habit(db_session, user_id)

    habit_service.log_habit(db_session, user_id, habit)
    habit_service.log_habit(db_session, user_id, habit)
    db_session.commit()

    assert db_session.get(GamificationState, user_id).xp_total == config.XP_HABIT_LOGGED
    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="habit_logged")
        .count()
        == 1
    )
