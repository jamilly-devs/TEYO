from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models.enums import JobApplicationStatus


class JobApplicationCreate(BaseModel):
    company: str
    role: str
    applied_on: Optional[date] = None
    notes: Optional[str] = None


class JobApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    applied_on: Optional[date] = None
    status: Optional[JobApplicationStatus] = None
    notes: Optional[str] = None


class JobApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    role: str
    applied_on: Optional[date]
    status: JobApplicationStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
