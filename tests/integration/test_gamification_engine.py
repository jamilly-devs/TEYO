"""gamification/engine.py — XP, nível e conquistas. Nenhuma função commita;
o teste commita para conferir a persistência."""

from datetime import datetime

from core import domain_events
from db.models.achievement import Achievement
from db.models.enums import TaskPriority, TaskStatus
from db.models.gamification import GamificationEvent, GamificationState
from db.models.task import Task
from gamification import config, engine

NOW = datetime(2026, 9, 9, 12, 0, 0)


def _done_task(db, user_id, priority=TaskPriority.MEDIUM, pomodoro_enabled=False):
    task = Task(
        user_id=user_id,
        title="t",
        status=TaskStatus.DONE,
        priority=priority,
        pomodoro_enabled=pomodoro_enabled,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def test_award_xp_writes_event_and_upserts_state(db_session, user_id):
    engine.award_xp(db_session, user_id, "task_completed", 10, now=NOW)
    db_session.commit()

    state = db_session.get(GamificationState, user_id)
    assert state.xp_total == 10
    assert state.level == 1
    assert db_session.query(GamificationEvent).filter_by(user_id=user_id).count() == 1


def test_task_completed_awards_base_xp(db_session, user_id):
    engine.apply_task_completed(db_session, user_id, _done_task(db_session, user_id), now=NOW)
    db_session.commit()
    assert db_session.get(GamificationState, user_id).xp_total == config.XP_TASK_COMPLETED


def test_high_effort_task_adds_bonus(db_session, user_id):
    task = _done_task(db_session, user_id, priority=TaskPriority.HIGH)
    engine.apply_task_completed(db_session, user_id, task, now=NOW)
    db_session.commit()
    expected = config.XP_TASK_COMPLETED + config.XP_TASK_HIGH_EFFORT_BONUS
    assert db_session.get(GamificationState, user_id).xp_total == expected


def test_level_up_event_emitted_on_threshold_crossing(db_session, user_id, monkeypatch):
    seen = []
    monkeypatch.setattr(
        domain_events, "emit", lambda name, **payload: seen.append((name, payload))
    )
    engine.award_xp(db_session, user_id, "manual", config.XP_PER_LEVEL, now=NOW)
    db_session.commit()

    assert any(
        name == domain_events.LEVEL_UP and payload.get("to_level") == 2
        for name, payload in seen
    )
    assert db_session.get(GamificationState, user_id).level == 2


def test_pomodoro_1_achievement_unlocks_once_and_grants_bonus(db_session, user_id):
    db_session.add(
        GamificationEvent(
            user_id=user_id, event_type="pomodoro_completed", xp_delta=20, created_at=NOW
        )
    )
    db_session.commit()

    first = engine.evaluate_achievements(db_session, user_id, now=NOW)
    db_session.commit()
    second = engine.evaluate_achievements(db_session, user_id, now=NOW)
    db_session.commit()

    assert "pomodoro_1" in first
    assert "pomodoro_1" not in second
    assert (
        db_session.query(Achievement).filter_by(user_id=user_id, code="pomodoro_1").count()
        == 1
    )
    assert (
        db_session.query(GamificationEvent)
        .filter_by(user_id=user_id, event_type="achievement_unlocked")
        .count()
        == 1
    )


def test_focus_day_achievement_after_three_high_effort_same_day(db_session, user_id):
    for _ in range(3):
        db_session.add(
            GamificationEvent(
                user_id=user_id,
                event_type="task_completed_high_effort",
                xp_delta=5,
                created_at=NOW,
            )
        )
    db_session.commit()
    assert "focus_day" in engine.evaluate_achievements(db_session, user_id, now=NOW)


def test_achievements_isolated_by_user(db_session, user_id, other_user_id):
    db_session.add(
        GamificationEvent(
            user_id=other_user_id,
            event_type="pomodoro_completed",
            xp_delta=20,
            created_at=NOW,
        )
    )
    db_session.commit()
    assert engine.evaluate_achievements(db_session, user_id, now=NOW) == []
