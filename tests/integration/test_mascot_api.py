def test_state_requires_authentication(client):
    assert client.get("/mascot/state").status_code == 401


def test_default_state_for_new_user(authenticated_client):
    body = authenticated_client.get("/mascot/state").json()
    assert body["evolution_stage"] == 1
    assert body["current_expression"] == "idle"
    assert body["color"].startswith("#")
    assert body["unlocked_features"] == []


def test_patch_color_changes_only_color(authenticated_client):
    response = authenticated_client.patch("/mascot/color", json={"color": "#123ABC"})
    assert response.status_code == 200
    assert response.json()["color"] == "#123ABC"

    # persistiu
    assert authenticated_client.get("/mascot/state").json()["color"] == "#123ABC"


def test_patch_color_rejects_non_hex(authenticated_client):
    assert authenticated_client.patch("/mascot/color", json={"color": "roxo"}).status_code == 422


def test_state_reacts_to_task_completion(authenticated_client):
    task = authenticated_client.post("/tasks", json={"title": "x"}).json()
    authenticated_client.post(f"/tasks/{task['id']}/complete")

    assert (
        authenticated_client.get("/mascot/state").json()["current_expression"] == "happy"
    )
