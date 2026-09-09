def test_state_requires_authentication(client):
    assert client.get("/gamification/state").status_code == 401


def test_state_defaults_for_new_user(authenticated_client):
    response = authenticated_client.get("/gamification/state")
    assert response.status_code == 200

    body = response.json()
    assert body["level"] == 1
    assert body["xp_total"] == 0
    assert body["xp_into_level"] == 0
    assert body["xp_for_next_level"] == 100
    assert body["streak_days"] == 0
    assert body["achievements"] == []


def test_state_reflects_completed_tasks(authenticated_client):
    task = authenticated_client.post("/tasks", json={"title": "x"}).json()
    authenticated_client.post(f"/tasks/{task['id']}/complete")

    body = authenticated_client.get("/gamification/state").json()
    assert body["xp_total"] == 10
    assert body["xp_into_level"] == 10
    # streak depende de fuso/relógio real — coberto de forma determinística
    # em test_gamification_streak.py; aqui só garantimos o campo presente.
    assert isinstance(body["streak_days"], int)
