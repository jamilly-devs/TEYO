from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models.enums import FinancialRecordType


class FinancialRecordCreate(BaseModel):
    type: FinancialRecordType
    amount: Decimal
    category: Optional[str] = None
    date: date
    description: Optional[str] = None


class FinancialRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: FinancialRecordType
    amount: Decimal
    category: Optional[str]
    date: date
    description: Optional[str]
    created_at: datetime
