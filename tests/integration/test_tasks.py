def test_create_task_uses_documented_defaults(authenticated_client):
    response = authenticated_client.post("/tasks", json={"title": "lavar louça"})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["priority"] == "medium"
    assert body["category"] is None
    assert body["is_recurring"] is False


def test_create_task_rejects_invalid_priority(authenticated_client):
    response = authenticated_client.post(
        "/tasks", json={"title": "x", "priority": "urgent"}
    )
    assert response.status_code == 422


def test_update_and_complete_task(authenticated_client):
    task = authenticated_client.post("/tasks", json={"title": "estudar inglês"}).json()

    response = authenticated_client.patch(
        f"/tasks/{task['id']}", json={"priority": "high", "category": "studies"}
    )
    assert response.status_code == 200
    assert response.json()["priority"] == "high"
    assert response.json()["category"] == "studies"

    response = authenticated_client.post(f"/tasks/{task['id']}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_delete_task_removes_it(authenticated_client):
    task = authenticated_client.post("/tasks", json={"title": "x"}).json()
    response = authenticated_client.delete(f"/tasks/{task['id']}")
    assert response.status_code == 204

    response = authenticated_client.get("/tasks")
    assert response.json() == []


def test_task_cannot_reference_another_users_goal(client):
    client.post("/auth/register", json={"email": "owner@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "owner@x.com", "password": "s3cret!"})
    goal = client.post("/goals", json={"title": "meta do dono"}).json()
    client.post("/auth/logout")

    client.post("/auth/register", json={"email": "intruder@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "intruder@x.com", "password": "s3cret!"})
    response = client.post("/tasks", json={"title": "x", "goal_id": goal["id"]})
    assert response.status_code == 404


def test_users_do_not_see_each_others_tasks(client):
    client.post("/auth/register", json={"email": "one@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "one@x.com", "password": "s3cret!"})
    client.post("/tasks", json={"title": "tarefa da user one"})
    client.post("/auth/logout")

    client.post("/auth/register", json={"email": "two@x.com", "password": "s3cret!"})
    client.post("/auth/login", json={"email": "two@x.com", "password": "s3cret!"})
    response = client.get("/tasks")
    assert response.json() == []
