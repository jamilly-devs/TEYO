"""Hábitos — API CRUD + /log (MODULES/HABITS.md, FASE 10)."""


def test_habits_require_authentication(client):
    assert client.get("/habits").status_code == 401


def test_create_habit_returns_streak_zero(authenticated_client):
    response = authenticated_client.post(
        "/habits", json={"title": "ler", "frequency_target": 3}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "ler"
    assert body["frequency_target"] == 3
    assert body["streak"] == 0


def test_frequency_target_out_of_range_is_rejected(authenticated_client):
    assert (
        authenticated_client.post(
            "/habits", json={"title": "x", "frequency_target": 8}
        ).status_code
        == 422
    )
    assert (
        authenticated_client.post(
            "/habits", json={"title": "x", "frequency_target": 0}
        ).status_code
        == 422
    )


def test_update_habit_fields(authenticated_client):
    habit = authenticated_client.post(
        "/habits", json={"title": "ler", "frequency_target": 3}
    ).json()

    response = authenticated_client.patch(
        f"/habits/{habit['id']}", json={"title": "ler 30min", "frequency_target": 5}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "ler 30min"
    assert response.json()["frequency_target"] == 5


def test_log_habit_is_idempotent_per_day(authenticated_client):
    habit = authenticated_client.post(
        "/habits", json={"title": "ler", "frequency_target": 3}
    ).json()

    first = authenticated_client.post(f"/habits/{habit['id']}/log")
    second = authenticated_client.post(f"/habits/{habit['id']}/log")

    assert first.status_code == 200
    assert second.status_code == 200
    # mesmo log devolvido — não cria um segundo
    assert first.json()["id"] == second.json()["id"]


def test_no_delete_endpoint(authenticated_client):
    habit = authenticated_client.post(
        "/habits", json={"title": "ler", "frequency_target": 3}
    ).json()
    assert authenticated_client.delete(f"/habits/{habit['id']}").status_code == 405


def test_habits_isolated_by_user(client):
    client.post("/auth/register", json={"email": "one@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "one@x.com", "password": "s3cret!"})
    other = client.post(
        "/habits", json={"title": "ler", "frequency_target": 3}
    ).json()
    client.post("/auth/logout")

    client.post("/auth/register", json={"email": "two@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "two@x.com", "password": "s3cret!"})
    assert client.get("/habits").json() == []
    assert client.post(f"/habits/{other['id']}/log").status_code == 404
