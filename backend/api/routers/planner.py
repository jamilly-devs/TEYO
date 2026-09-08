from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.planner import DailyPlanItemOut, DailyPlanOut, ReorganizeRequest
from db.models.user import User
from db.session import get_db
from planner.daily_plan import DailyPlan, compute_daily_plan, compute_reorganized_plan

router = APIRouter(prefix="/planner", tags=["planner"])


def _to_out(plan: DailyPlan) -> DailyPlanOut:
    return DailyPlanOut(
        date=plan.plan_date,
        items=[DailyPlanItemOut.model_validate(item) for item in plan.items],
    )


@router.get("/daily-plan", response_model=DailyPlanOut)
def get_daily_plan(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> DailyPlanOut:
    return _to_out(compute_daily_plan(db, user))


@router.post("/reorganize", response_model=DailyPlanOut)
def reorganize(
    payload: ReorganizeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DailyPlanOut:
    return _to_out(compute_reorganized_plan(db, user, energy_level=payload.energy_level))
