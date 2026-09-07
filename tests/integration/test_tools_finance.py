import pytest

from tools.errors import ToolValidationError
from tools.finance import create_financial_record, list_financial_records


def test_create_financial_record_requires_type_amount_and_date(db_session, user_id):
    with pytest.raises(ToolValidationError):
        create_financial_record(db_session, user_id, {})
    with pytest.raises(ToolValidationError):
        create_financial_record(db_session, user_id, {"type": "expense"})


def test_create_financial_record_rejects_undocumented_type(db_session, user_id):
    with pytest.raises(ToolValidationError):
        create_financial_record(
            db_session, user_id, {"type": "transfer", "amount": 10, "date": "2026-09-04"}
        )


def test_create_financial_record_persists(db_session, user_id):
    result = create_financial_record(
        db_session, user_id, {"type": "expense", "amount": 42.5, "date": "2026-09-04"}
    )
    assert result["type"] == "expense"
    assert float(result["amount"]) == 42.5


def test_list_financial_records_only_returns_owner_records(db_session, user_id, other_user_id):
    create_financial_record(
        db_session, user_id, {"type": "income", "amount": 100, "date": "2026-09-04"}
    )
    create_financial_record(
        db_session, other_user_id, {"type": "income", "amount": 999, "date": "2026-09-04"}
    )
    assert len(list_financial_records(db_session, user_id, {})["items"]) == 1
