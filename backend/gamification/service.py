"""Leitura do estado de gamificação para a API e para a tool
`get_gamification_state`. Os números vêm sempre da persistência
(`gamification_state` / `gamification_events` / `achievements`), nunca de
estimativa — `BUSINESS_RULES.md` #6/#7, `GAMIFICATION.md`.
"""

from typing import Any

from sqlalchemy.orm import Session

from db.models.achievement import Achievement
from db.models.gamification import GamificationState
from gamification import config
from gamification.streak import current_streak

_CATALOG = {spec.code: spec for spec in config.ACHIEVEMENTS}


def get_state(db: Session, user_id: int) -> dict[str, Any]:
    state = db.get(GamificationState, user_id)
    xp_total = state.xp_total if state is not None else 0
    level = state.level if state is not None else 1
    xp_into_level, xp_for_next_level = config.xp_progress(xp_total)

    achievements = (
        db.query(Achievement)
        .filter_by(user_id=user_id)
        .order_by(Achievement.unlocked_at, Achievement.id)
        .all()
    )
    return {
        "xp_total": xp_total,
        "level": level,
        "xp_into_level": xp_into_level,
        "xp_for_next_level": xp_for_next_level,
        "streak_days": current_streak(db, user_id),
        "achievements": [
            {
                "code": row.code,
                "title": _CATALOG[row.code].title if row.code in _CATALOG else row.code,
                "description": (
                    _CATALOG[row.code].description if row.code in _CATALOG else ""
                ),
                "unlocked_at": row.unlocked_at.isoformat(),
            }
            for row in achievements
        ],
    }
