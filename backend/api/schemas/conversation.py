from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from db.models.enums import MessageRole


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: MessageRole
    content: str
    created_at: datetime
