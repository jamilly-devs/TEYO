from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.gamification import GamificationStateOut
from db.models.user import User
from db.session import get_db
from gamification.service import get_state

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/state", response_model=GamificationStateOut)
def read_state(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    """XP, nível, streak e conquistas — sempre do sistema, nunca estimados
    (`BUSINESS_RULES.md` #6/#7, `GAMIFICATION.md`)."""
    return get_state(db, user.id)
