from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.planner import DailyPlanOut, ReorganizeRequest
from core.domain_events import on_low_energy_reported
from db.models.user import User
from db.session import get_db
from planner.daily_plan import compute_daily_plan, compute_reorganized_plan
from planner.serialization import serialize_plan

router = APIRouter(prefix="/planner", tags=["planner"])


@router.get("/daily-plan", response_model=DailyPlanOut)
def get_daily_plan(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    return serialize_plan(compute_daily_plan(db, user))


@router.post("/reorganize", response_model=DailyPlanOut)
def reorganize(
    payload: ReorganizeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    plan = compute_reorganized_plan(db, user, energy_level=payload.energy_level)
    if payload.energy_level == "low":
        # Mesmo sinal da tool `reorganize_day`. FASE 9: o mascote reage e
        # persiste `mascot_state` — commit aqui, como quem chama. Não muda
        # o corpo da resposta.
        on_low_energy_reported(db, user.id)
        db.commit()
    return serialize_plan(plan)
