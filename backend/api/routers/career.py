from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.career import (
    JobApplicationCreate,
    JobApplicationOut,
    JobApplicationUpdate,
)
from db.models.job_application import JobApplication
from db.models.user import User
from db.session import get_db

router = APIRouter(prefix="/career", tags=["career"])


def _get_owned_application(app_id: int, user: User, db: Session) -> JobApplication:
    application = db.get(JobApplication, app_id)
    if application is None or application.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="job application not found"
        )
    return application


@router.get("/applications", response_model=List[JobApplicationOut])
def list_applications(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[JobApplication]:
    return db.query(JobApplication).filter_by(user_id=user.id).all()


@router.post(
    "/applications", response_model=JobApplicationOut, status_code=status.HTTP_201_CREATED
)
def create_application(
    payload: JobApplicationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobApplication:
    application = JobApplication(user_id=user.id, **payload.model_dump(exclude_unset=True))
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.patch("/applications/{app_id}", response_model=JobApplicationOut)
def update_application(
    app_id: int,
    payload: JobApplicationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobApplication:
    application = _get_owned_application(app_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    application.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    return application
