"""Carreira — acompanhamento manual de candidaturas (MODULES/CAREER.md,
FASE 10). CRUD simples espelhando Objetivos; sem busca de vagas, sem
DELETE."""


def test_state_requires_authentication(client):
    assert client.get("/career/applications").status_code == 401


def test_create_defaults_status_interested(authenticated_client):
    response = authenticated_client.post(
        "/career/applications", json={"company": "Acme", "role": "QA Engineer"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "interested"
    assert body["company"] == "Acme"
    assert body["role"] == "QA Engineer"
    assert body["applied_on"] is None


def test_create_requires_company_and_role(authenticated_client):
    assert (
        authenticated_client.post("/career/applications", json={"company": "Acme"}).status_code
        == 422
    )


def test_update_status_and_fields(authenticated_client):
    created = authenticated_client.post(
        "/career/applications", json={"company": "Acme", "role": "QA"}
    ).json()

    response = authenticated_client.patch(
        f"/career/applications/{created['id']}",
        json={"status": "interviewing", "notes": "entrevista dia 20"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "interviewing"
    assert body["notes"] == "entrevista dia 20"


def test_update_rejects_invalid_status(authenticated_client):
    created = authenticated_client.post(
        "/career/applications", json={"company": "Acme", "role": "QA"}
    ).json()
    response = authenticated_client.patch(
        f"/career/applications/{created['id']}", json={"status": "hired"}
    )
    assert response.status_code == 422


def test_no_delete_endpoint(authenticated_client):
    created = authenticated_client.post(
        "/career/applications", json={"company": "Acme", "role": "QA"}
    ).json()
    assert (
        authenticated_client.delete(f"/career/applications/{created['id']}").status_code == 405
    )


def test_applications_isolated_by_user(client):
    client.post("/auth/register", json={"email": "one@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "one@x.com", "password": "s3cret!"})
    other = client.post(
        "/career/applications", json={"company": "Acme", "role": "QA"}
    ).json()
    client.post("/auth/logout")

    client.post("/auth/register", json={"email": "two@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "two@x.com", "password": "s3cret!"})
    assert client.get("/career/applications").json() == []
    assert client.patch(
        f"/career/applications/{other['id']}", json={"status": "applied"}
    ).status_code == 404
