def test_create_and_list_financial_record(authenticated_client):
    response = authenticated_client.post(
        "/finance/records",
        json={"type": "expense", "amount": "42.50", "date": "2026-09-04"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "expense"
    assert body["amount"] == "42.50"

    response = authenticated_client.get("/finance/records")
    assert len(response.json()) == 1


def test_create_financial_record_rejects_undocumented_type(authenticated_client):
    response = authenticated_client.post(
        "/finance/records",
        json={"type": "transfer", "amount": "1", "date": "2026-09-04"},
    )
    assert response.status_code == 422
