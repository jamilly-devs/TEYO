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


def test_daily_plan_endpoint_keeps_tools_md_contract(authenticated_client):
    authenticated_client.post("/tasks", json={"title": "estudar", "priority": "high"})

    body = authenticated_client.get("/planner/daily-plan").json()

    assert set(body) == {"date", "items"}
    assert set(body["items"][0]) == {
        "kind",
        "id",
        "title",
        "period",
        "start_at",
        "priority",
        "reason",
        "suggested_due_date",
    }


def test_reorganize_endpoint_emits_low_energy_signal_only_for_low(
    authenticated_client, monkeypatch
):
    calls = []
    monkeypatch.setattr(
        "api.routers.planner.on_low_energy_reported", lambda db, uid: calls.append(uid)
    )
    authenticated_client.post("/tasks", json={"title": "pesada", "priority": "high"})

    authenticated_client.post("/planner/reorganize", json={"energy_level": "low"})
    assert len(calls) == 1

    authenticated_client.post("/planner/reorganize", json={"energy_level": "high"})
    authenticated_client.post("/planner/reorganize", json={})
    assert len(calls) == 1
