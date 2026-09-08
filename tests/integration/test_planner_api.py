def test_daily_plan_endpoint_lists_unanchored_task(authenticated_client):
    authenticated_client.post("/tasks", json={"title": "estudar", "priority": "high"})

    response = authenticated_client.get("/planner/daily-plan")

    assert response.status_code == 200
    body = response.json()
    assert "date" in body
    assert [item["title"] for item in body["items"]] == ["estudar"]


def test_daily_plan_endpoint_requires_authentication(client):
    response = client.get("/planner/daily-plan")
    assert response.status_code == 401


def test_reorganize_endpoint_defers_high_priority_task_under_low_energy(authenticated_client):
    authenticated_client.post("/tasks", json={"title": "leve", "priority": "low"})
    authenticated_client.post("/tasks", json={"title": "pesada", "priority": "high"})

    response = authenticated_client.post("/planner/reorganize", json={"energy_level": "low"})

    assert response.status_code == 200
    items = response.json()["items"]
    titles = [item["title"] for item in items]
    assert titles.index("pesada") > titles.index("leve")
    pesada = next(item for item in items if item["title"] == "pesada")
    assert pesada["reason"] is not None
    assert pesada["suggested_due_date"] is not None


def test_reorganize_endpoint_without_energy_level_matches_daily_plan(authenticated_client):
    authenticated_client.post("/tasks", json={"title": "tarefa", "priority": "medium"})

    plan = authenticated_client.get("/planner/daily-plan").json()
    reorganized = authenticated_client.post("/planner/reorganize", json={}).json()

    assert reorganized["items"] == plan["items"]
