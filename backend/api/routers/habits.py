from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.habit import (
    HabitCreate,
    HabitLogOut,
    HabitUpdate,
    HabitWithStreakOut,
)
from db.models.habit import Habit
from db.models.user import User
from db.session import get_db
from habits.service import log_habit
from habits.streak import individual_streak

router = APIRouter(prefix="/habits", tags=["habits"])


def _get_owned_habit(habit_id: int, user: User, db: Session) -> Habit:
    habit = db.get(Habit, habit_id)
    if habit is None or habit.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="habit not found")
    return habit


def _with_streak(db: Session, habit: Habit) -> dict[str, Any]:
    return {
        "id": habit.id,
        "title": habit.title,
        "frequency_target": habit.frequency_target,
        "created_at": habit.created_at,
        "streak": individual_streak(db, habit.id),
    }


@router.get("", response_model=List[HabitWithStreakOut])
def list_habits(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[dict]:
    return [_with_streak(db, h) for h in db.query(Habit).filter_by(user_id=user.id).all()]


@router.post("", response_model=HabitWithStreakOut, status_code=status.HTTP_201_CREATED)
def create_habit(
    payload: HabitCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    habit = Habit(user_id=user.id, **payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return _with_streak(db, habit)


@router.patch("/{habit_id}", response_model=HabitWithStreakOut)
def update_habit(
    habit_id: int,
    payload: HabitUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    habit = _get_owned_habit(habit_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    # `habits` não tem coluna `updated_at` (schema FASE 1, DT-13) — nada a bumpar.
    db.commit()
    db.refresh(habit)
    return _with_streak(db, habit)


@router.post("/{habit_id}/log", response_model=HabitLogOut)
def create_habit_log(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    habit = _get_owned_habit(habit_id, user, db)
    result = log_habit(db, user.id, habit)
    db.commit()
    return result["log"]
