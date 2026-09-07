"""Tools de Mercado (MODULES/MARKET.md, TOOLS.md).

`remove_market_item` = hard delete, distinto de marcar `status=purchased`
(feito pela tela via PATCH). Decisão já registrada no código da FASE 2
(`api/routers/market.py`) e sincronizada na documentação nesta fase — ver
`DOCUMENTATION_AUDIT.md`."""

from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.schemas.market import MarketItemCreate, MarketItemOut
from db.models.market import MarketItem
from llm.base import ToolSpec
from tools.base import ToolDefinition
from tools.errors import ToolNotFoundError, ToolValidationError, format_validation_error, require_id


def _get_owned_item(db: Session, user_id: int, item_id: int) -> MarketItem:
    item = db.get(MarketItem, item_id)
    if item is None or item.user_id != user_id:
        raise ToolNotFoundError(f"item de mercado {item_id} não encontrado")
    return item


def _serialize(item: MarketItem) -> dict[str, Any]:
    return MarketItemOut.model_validate(item).model_dump(mode="json")


def add_market_item(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = MarketItemCreate(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    item = MarketItem(user_id=user_id, **payload.model_dump(exclude_unset=True))
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


def remove_market_item(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    item_id = require_id(arguments, "item_id")
    item = _get_owned_item(db, user_id, item_id)
    db.delete(item)
    db.commit()
    return {"deleted": True, "item_id": item_id}


def list_market_items(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    items = db.query(MarketItem).filter_by(user_id=user_id).all()
    return {"items": [_serialize(item) for item in items]}


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="add_market_item",
            description="Adiciona um item à lista de mercado do usuário.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                },
                "required": ["name"],
            },
        ),
        execute=add_market_item,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="remove_market_item",
            description=(
                "Remove um item da lista de mercado (exclusão definitiva, "
                "não é a mesma ação de marcar como comprado). AÇÃO "
                "DESTRUTIVA: só chame depois que o usuário confirmar "
                "explicitamente, na conversa, que quer remover este item "
                "específico da lista."
            ),
            parameters={
                "type": "object",
                "properties": {"item_id": {"type": "integer"}},
                "required": ["item_id"],
            },
        ),
        execute=remove_market_item,
        destructive=True,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="list_market_items",
            description=(
                "Lista os itens existentes na lista de mercado do usuário. "
                "Use para consultar ou resolver a qual item uma mensagem "
                "ambígua se refere antes de chamar remove_market_item."
            ),
            parameters={"type": "object", "properties": {}},
        ),
        execute=list_market_items,
    ),
]
