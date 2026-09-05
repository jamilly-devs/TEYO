def test_register_login_logout_flow(client):
    register_payload = {"email": "a@b.com", "password": "s3cret!", "name": "A"}
    response = client.post("/auth/register", json=register_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "a@b.com"
    assert "password" not in body
    assert "password_hash" not in body

    response = client.post(
        "/auth/login", json={"email": "a@b.com", "password": "s3cret!"}
    )
    assert response.status_code == 200
    assert "teyo_session" in response.cookies

    response = client.get("/tasks")
    assert response.status_code == 200

    response = client.post("/auth/logout")
    assert response.status_code == 204

    response = client.get("/tasks")
    assert response.status_code == 401


def test_login_with_wrong_password_is_rejected(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "s3cret!"})
    response = client.post("/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert response.status_code == 401


def test_duplicate_registration_is_rejected(client):
    payload = {"email": "a@b.com", "password": "s3cret!"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_protected_route_without_session_is_rejected(client):
    response = client.get("/tasks")
    assert response.status_code == 401


def test_me_restores_session_after_login(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "a@b.com", "password": "s3cret!"})

    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "a@b.com"


def test_me_without_session_is_rejected(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
