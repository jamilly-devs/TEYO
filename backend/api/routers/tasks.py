from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.task import TaskCreate, TaskOut, TaskUpdate
from core import task_completion
from db.models.enums import TaskStatus
from db.models.goal import Goal
from db.models.task import Task
from db.models.user import User
from db.session import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_owned_task(task_id: int, user: User, db: Session) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    return task


def _validate_goal_ownership(goal_id: int, user: User, db: Session) -> None:
    goal = db.get(Goal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="goal not found")


@router.get("", response_model=List[TaskOut])
def list_tasks(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[Task]:
    return db.query(Task).filter_by(user_id=user.id).all()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Task:
    if payload.goal_id is not None:
        _validate_goal_ownership(payload.goal_id, user, db)

    fields = payload.model_dump(exclude_unset=True)
    task = Task(user_id=user.id, **fields)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Task:
    task = _get_owned_task(task_id, user, db)

    fields = payload.model_dump(exclude_unset=True)
    if "goal_id" in fields and fields["goal_id"] is not None:
        _validate_goal_ownership(fields["goal_id"], user, db)

    # `status=done` via PATCH é um dos quatro caminhos de conclusão — passa
    # pelo mesmo ponto único que `POST /{id}/complete` (ver
    # core/task_completion.py).
    completing = (
        fields.get("status") == TaskStatus.DONE and task.status != TaskStatus.DONE
    )
    for field, value in fields.items():
        if completing and field == "status":
            continue
        setattr(task, field, value)
    if completing:
        task_completion.complete_task(db, user.id, task)
    else:
        task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    task = _get_owned_task(task_id, user, db)
    db.delete(task)
    db.commit()


@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(
    task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Task:
    task = _get_owned_task(task_id, user, db)
    task_completion.complete_task(db, user.id, task)
    db.commit()
    db.refresh(task)
    return task
