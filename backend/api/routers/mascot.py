from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.mascot import MascotColorUpdate, MascotStateOut
from db.models.user import User
from db.session import get_db
from mascot.service import get_state, set_color

router = APIRouter(prefix="/mascot", tags=["mascot"])


@router.get("/state", response_model=MascotStateOut)
def read_state(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    return get_state(db, user.id)


@router.patch("/color", response_model=MascotStateOut)
def update_color(
    payload: MascotColorUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Única personalização visual disponível ao usuário
    (`BUSINESS_RULES.md` #10)."""
    result = set_color(db, user.id, payload.color)
    db.commit()
    return result
