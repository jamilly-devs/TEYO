"""mascot/engine.py — estado do mascote derivado do sistema. Estágio vem
do NÍVEL (DECISÃO C); expressão volta a `idle` após o TTL; features vêm
das conquistas."""

from datetime import datetime

from db.models.achievement import Achievement
from db.models.gamification import GamificationState
from db.models.mascot import MascotState
from mascot import catalog, engine


def test_resolve_state_defaults_without_row(db_session, user_id):
    state = engine.resolve_state(db_session, user_id)
    assert state["evolution_stage"] == 1
    assert state["current_expression"] == "idle"
    assert state["color"] == catalog.DEFAULT_COLOR
    assert state["unlocked_features"] == []


def test_stage_is_derived_from_level(db_session, user_id):
    db_session.add(GamificationState(user_id=user_id, xp_total=0, level=7))
    db_session.commit()
    assert engine.resolve_state(db_session, user_id)["evolution_stage"] == 3


def test_expression_reverts_to_idle_after_ttl(db_session, user_id):
    engine.set_expression(
        db_session, user_id, "happy", now=datetime(2026, 9, 9, 10, 0, 0)
    )
    db_session.commit()

    fresh = engine.resolve_state(db_session, user_id, now=datetime(2026, 9, 9, 10, 30, 0))
    stale = engine.resolve_state(db_session, user_id, now=datetime(2026, 9, 9, 23, 0, 0))

    assert fresh["current_expression"] == "happy"
    assert stale["current_expression"] == "idle"


def test_unlocked_features_come_from_achievements(db_session, user_id):
    db_session.add(
        Achievement(user_id=user_id, code="streak_7", unlocked_at=datetime.utcnow())
    )
    db_session.commit()
    assert "item_scarf" in engine.resolve_state(db_session, user_id)["unlocked_features"]


def test_set_color_changes_only_color(db_session, user_id):
    engine.set_expression(db_session, user_id, "proud")
    db_session.commit()
    engine.set_color(db_session, user_id, "#abc")
    db_session.commit()

    row = db_session.get(MascotState, user_id)
    assert row.color == "#abc"
    assert row.current_expression == "proud"


def test_recompute_stage_caches_on_row(db_session, user_id):
    engine.recompute_stage(db_session, user_id, 12)
    db_session.commit()
    assert db_session.get(MascotState, user_id).evolution_stage == 4
