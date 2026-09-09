"""tool get_gamification_state — só leitura; devolve o que está persistido,
nunca uma estimativa (BUSINESS_RULES.md #6/#7, GAMIFICATION.md)."""

from gamification.engine import award_xp
from gamification.tools import get_gamification_state


def test_returns_defaults_for_new_user(db_session, user_id):
    result = get_gamification_state(db_session, user_id, {})
    assert result["level"] == 1
    assert result["xp_total"] == 0
    assert result["xp_for_next_level"] == 100
    assert result["achievements"] == []


def test_reflects_persisted_state(db_session, user_id):
    award_xp(db_session, user_id, "manual", 130)
    db_session.commit()

    result = get_gamification_state(db_session, user_id, {})
    assert result["xp_total"] == 130
    assert result["level"] == 2
    assert result["xp_into_level"] == 30


def test_isolated_by_user(db_session, user_id, other_user_id):
    award_xp(db_session, other_user_id, "manual", 50)
    db_session.commit()
    assert get_gamification_state(db_session, user_id, {})["xp_total"] == 0
