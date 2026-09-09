"""Regras que determinam o estado do mascote a partir de eventos do
sistema.

Separação (decisão FASE 9):
- ESTADO: tabela `mascot_state` (cor, estágio, expressão) + `achievements`.
- REGRAS: este módulo (o que cada evento faz com o estado).
- RENDERIZAÇÃO: frontend (`components/Mascot.tsx`) — não tem lógica.

`resolve_state` é a leitura canônica (API e testes): o estágio é sempre
derivado do NÍVEL (DECISÃO C — `mascot_state.evolution_stage` é só cache),
a expressão volta a `idle` depois do TTL, e `unlocked_features` sai das
conquistas via `catalog`. Nenhuma função commita (regra FASE 8)."""

from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from db.models.achievement import Achievement
from db.models.gamification import GamificationState
from db.models.mascot import MascotState
from mascot import catalog


def _get_or_create(db: Session, user_id: int) -> MascotState:
    state = db.get(MascotState, user_id)
    if state is None:
        state = MascotState(user_id=user_id, evolution_stage=1)
        db.add(state)
        db.flush()
    return state


def _user_level(db: Session, user_id: int) -> int:
    gami = db.get(GamificationState, user_id)
    return gami.level if gami is not None else 1


def set_expression(
    db: Session, user_id: int, expression: str, now: Optional[datetime] = None
) -> None:
    state = _get_or_create(db, user_id)
    state.current_expression = expression
    state.updated_at = now or datetime.utcnow()
    db.flush()


def recompute_stage(db: Session, user_id: int, level: int) -> None:
    """Cache do estágio na linha (a verdade é `catalog.stage_for_level`)."""
    state = _get_or_create(db, user_id)
    state.evolution_stage = catalog.stage_for_level(level)
    state.updated_at = datetime.utcnow()
    db.flush()


def _achievement_codes(db: Session, user_id: int) -> list[str]:
    rows = (
        db.query(Achievement)
        .filter_by(user_id=user_id)
        .order_by(Achievement.unlocked_at, Achievement.id)
        .all()
    )
    return [row.code for row in rows]


def resolve_state(
    db: Session, user_id: int, now: Optional[datetime] = None
) -> dict[str, Any]:
    now = now or datetime.utcnow()
    state = db.get(MascotState, user_id)
    stage = catalog.stage_for_level(_user_level(db, user_id))

    if state is None:
        color = catalog.DEFAULT_COLOR
        expression = catalog.DEFAULT_EXPRESSION
        updated_at = None
    else:
        color = state.color or catalog.DEFAULT_COLOR
        expression = state.current_expression or catalog.DEFAULT_EXPRESSION
        updated_at = state.updated_at
        if updated_at is not None and now - updated_at > timedelta(
            minutes=catalog.EXPRESSION_TTL_MIN
        ):
            expression = catalog.DEFAULT_EXPRESSION

    return {
        "evolution_stage": stage,
        "current_expression": expression,
        "color": color,
        "unlocked_features": catalog.features_for_achievements(
            _achievement_codes(db, user_id)
        ),
        "updated_at": updated_at.isoformat() if updated_at is not None else None,
    }


def set_color(db: Session, user_id: int, color: str) -> dict[str, Any]:
    state = _get_or_create(db, user_id)
    state.color = color
    state.updated_at = datetime.utcnow()
    db.flush()
    return resolve_state(db, user_id)
