from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.schemas.market import MarketItemCreate, MarketItemOut, MarketItemStatusUpdate
from db.models.market import MarketItem
from db.models.user import User
from db.session import get_db

router = APIRouter(prefix="/market", tags=["market"])


def _get_owned_item(item_id: int, user: User, db: Session) -> MarketItem:
    item = db.get(MarketItem, item_id)
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="market item not found")
    return item


@router.get("", response_model=List[MarketItemOut])
def list_market_items(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> List[MarketItem]:
    return db.query(MarketItem).filter_by(user_id=user.id).all()


@router.post("/items", response_model=MarketItemOut, status_code=status.HTTP_201_CREATED)
def add_market_item(
    payload: MarketItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketItem:
    item = MarketItem(user_id=user.id, **payload.model_dump(exclude_unset=True))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/items/{item_id}", response_model=MarketItemOut)
def update_market_item_status(
    item_id: int,
    payload: MarketItemStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketItem:
    item = _get_owned_item(item_id, user, db)
    item.status = payload.status
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_market_item(
    item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    """Hard delete — per Jams's decision, distinct from marking `status=purchased`
    via the PATCH endpoint above."""
    item = _get_owned_item(item_id, user, db)
    db.delete(item)
    db.commit()
