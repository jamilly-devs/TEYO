from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.goal import GoalCreate, GoalOut, GoalUpdate
from db.models.goal import Goal
from db.models.user import User
from db.session import get_db

router = APIRouter(prefix="/goals", tags=["goals"])


def _get_owned_goal(goal_id: int, user: User, db: Session) -> Goal:
    goal = db.get(Goal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="goal not found")
    return goal


@router.get("", response_model=List[GoalOut])
def list_goals(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[Goal]:
    return db.query(Goal).filter_by(user_id=user.id).all()


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Goal:
    goal = Goal(user_id=user.id, **payload.model_dump(exclude_unset=True))
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.patch("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Goal:
    goal = _get_owned_goal(goal_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal
