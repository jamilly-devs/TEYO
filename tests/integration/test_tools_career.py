import pytest

from tools.career import (
    create_job_application,
    list_job_applications,
    update_job_application,
)
from tools.errors import ToolNotFoundError, ToolValidationError


def test_create_requires_company_and_role(db_session, user_id):
    with pytest.raises(ToolValidationError):
        create_job_application(db_session, user_id, {"company": "Acme"})


def test_create_and_list(db_session, user_id):
    result = create_job_application(
        db_session, user_id, {"company": "Acme", "role": "QA", "notes": "indicação"}
    )
    assert result["id"] is not None
    assert result["status"] == "interested"

    listed = list_job_applications(db_session, user_id, {})
    assert [a["company"] for a in listed["items"]] == ["Acme"]


def test_update_status(db_session, user_id):
    created = create_job_application(db_session, user_id, {"company": "Acme", "role": "QA"})
    updated = update_job_application(
        db_session, user_id, {"application_id": created["id"], "status": "applied"}
    )
    assert updated["status"] == "applied"


def test_update_missing_id_is_rejected(db_session, user_id):
    with pytest.raises(ToolValidationError):
        update_job_application(db_session, user_id, {"status": "applied"})


def test_update_other_users_application_is_not_found(db_session, user_id, other_user_id):
    created = create_job_application(
        db_session, other_user_id, {"company": "Acme", "role": "QA"}
    )
    with pytest.raises(ToolNotFoundError):
        update_job_application(
            db_session, user_id, {"application_id": created["id"], "status": "applied"}
        )


def test_list_only_returns_owner_applications(db_session, user_id, other_user_id):
    create_job_application(db_session, user_id, {"company": "Minha", "role": "QA"})
    create_job_application(db_session, other_user_id, {"company": "Alheia", "role": "QA"})

    result = list_job_applications(db_session, user_id, {})
    assert [a["company"] for a in result["items"]] == ["Minha"]
