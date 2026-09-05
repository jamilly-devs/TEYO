from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models.enums import MarketItemStatus


class MarketItemCreate(BaseModel):
    name: str
    category: Optional[str] = None


class MarketItemStatusUpdate(BaseModel):
    """`API.md` documents this endpoint as `PATCH /market/items/{id} (status)` —
    a status transition, not a generic field editor. No other field of
    `market_items` has a documented post-creation edit path."""

    status: MarketItemStatus


class MarketItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Optional[str]
    is_recurring_suggestion: bool
    status: MarketItemStatus
    created_at: datetime
