"""Tools de Finanças (MODULES/FINANCE.md, TOOLS.md).

`create_financial_record` não estava na lista-base de `TOOLS.md`; o nome e
o contrato foram definidos aqui seguindo exatamente o mesmo padrão das
outras tools de escrita (MODULES/FINANCE.md já delega essa decisão à
implementação). Sem update/delete: `API.md` só define GET/POST para
`/finance/records`."""

from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.schemas.finance import FinancialRecordCreate, FinancialRecordOut
from db.models.enums import FinancialRecordType
from db.models.finance import FinancialRecord
from llm.base import ToolSpec
from tools.base import ToolDefinition
from tools.errors import ToolValidationError, format_validation_error


def _serialize(record: FinancialRecord) -> dict[str, Any]:
    return FinancialRecordOut.model_validate(record).model_dump(mode="json")


def create_financial_record(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    """Cálculos financeiros pertencem ao sistema — esta tool só registra o
    dado bruto informado pelo usuário; nenhum total é calculado aqui
    (BUSINESS_RULES.md #7)."""
    try:
        payload = FinancialRecordCreate(**arguments)
    except ValidationError as exc:
        raise ToolValidationError(format_validation_error(exc)) from exc

    record = FinancialRecord(user_id=user_id, **payload.model_dump(exclude_unset=True))
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


def list_financial_records(db: Session, user_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    records = db.query(FinancialRecord).filter_by(user_id=user_id).all()
    return {"items": [_serialize(record) for record in records]}


DEFINITIONS = [
    ToolDefinition(
        spec=ToolSpec(
            name="create_financial_record",
            description="Registra um lançamento financeiro (receita ou despesa) do usuário.",
            parameters={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": [t.value for t in FinancialRecordType]},
                    "amount": {"type": "number"},
                    "category": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                    "description": {"type": "string"},
                },
                "required": ["type", "amount", "date"],
            },
        ),
        execute=create_financial_record,
    ),
    ToolDefinition(
        spec=ToolSpec(
            name="list_financial_records",
            description="Lista os lançamentos financeiros existentes do usuário.",
            parameters={"type": "object", "properties": {}},
        ),
        execute=list_financial_records,
    ),
]
