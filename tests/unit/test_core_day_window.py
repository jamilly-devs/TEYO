"""core/day_window.py — fronteira de dia no fuso do usuário e divisão do
dia em períodos (extraído de planner/daily_plan.py na completude da
FASE 8; a divisão de período tem que continuar idêntica à de
pattern_engine/task_time_of_day.py)."""

from datetime import date, datetime

import pytest

from core.day_window import PERIOD_ORDER, day_bounds, local_today, period_for_hour
from db.models.user import User


def _user(timezone="America/Sao_Paulo") -> User:
    return User(email="x@example.com", password_hash="x", timezone=timezone)


@pytest.mark.parametrize(
    "hour,expected",
    [
        (0, "madrugada"),
        (5, "madrugada"),
        (6, "manhã"),
        (11, "manhã"),
        (12, "tarde"),
        (17, "tarde"),
        (18, "noite"),
        (23, "noite"),
    ],
)
def test_period_for_hour_boundaries(hour, expected):
    assert period_for_hour(hour) == expected


def test_period_for_hour_rejects_out_of_range():
    with pytest.raises(AssertionError):
        period_for_hour(24)


def test_period_order_matches_pattern_engine_division():
    # pattern_engine/task_time_of_day.py não é tocado na FASE 8 — se a
    # ordem/os nomes divergirem, o Plano do Dia e os padrões passam a
    # falar de períodos diferentes.
    from pattern_engine.task_time_of_day import _PERIODS

    assert PERIOD_ORDER == tuple(label for _, label in _PERIODS)
    for hours, label in _PERIODS:
        for hour in hours:
            assert period_for_hour(hour) == label


def test_local_today_uses_explicit_now_as_already_in_user_tz():
    now = datetime(2026, 9, 7, 23, 30, 0)
    assert local_today(_user("Pacific/Kiritimati"), now=now) == date(2026, 9, 7)


def test_local_today_without_now_resolves_in_user_timezone():
    # Sem `now`, cai na hora real: só garantimos que devolve uma data e
    # que fusos muito distantes podem devolver datas diferentes no mesmo
    # instante — sem travar o relógio do teste.
    today_sp = local_today(_user("America/Sao_Paulo"))
    today_syd = local_today(_user("Australia/Sydney"))
    assert isinstance(today_sp, date)
    assert (today_syd - today_sp).days in (0, 1)


def test_day_bounds_spans_full_local_day():
    now = datetime(2026, 9, 7, 8, 0, 0)
    start, end = day_bounds(_user(), now=now)
    assert start == datetime(2026, 9, 7, 0, 0, 0, 0)
    assert end == datetime(2026, 9, 7, 23, 59, 59, 999999)
