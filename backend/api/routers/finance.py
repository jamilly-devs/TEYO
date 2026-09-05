from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.finance import FinancialRecordCreate, FinancialRecordOut
from db.models.finance import FinancialRecord
from db.models.user import User
from db.session import get_db

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/records", response_model=List[FinancialRecordOut])
def list_financial_records(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[FinancialRecord]:
    return db.query(FinancialRecord).filter_by(user_id=user.id).all()


@router.post("/records", response_model=FinancialRecordOut, status_code=status.HTTP_201_CREATED)
def create_financial_record(
    payload: FinancialRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FinancialRecord:
    record = FinancialRecord(user_id=user.id, **payload.model_dump(exclude_unset=True))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
