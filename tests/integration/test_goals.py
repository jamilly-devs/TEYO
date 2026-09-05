def test_create_goal_defaults_status_active(authenticated_client):
    response = authenticated_client.post("/goals", json={"title": "aprender inglês"})
    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_update_goal_status(authenticated_client):
    goal = authenticated_client.post("/goals", json={"title": "x"}).json()
    response = authenticated_client.patch(f"/goals/{goal['id']}", json={"status": "completed"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_goal_has_no_delete_endpoint(authenticated_client):
    goal = authenticated_client.post("/goals", json={"title": "x"}).json()
    response = authenticated_client.delete(f"/goals/{goal['id']}")
    assert response.status_code == 405
