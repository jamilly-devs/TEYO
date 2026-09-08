def test_create_event_defaults_source_to_manual(authenticated_client):
    response = authenticated_client.post(
        "/events",
        json={
            "title": "reunião",
            "start_at": "2026-09-10T14:00:00",
            "end_at": "2026-09-10T15:00:00",
        },
    )
    assert response.status_code == 201
    assert response.json()["source"] == "manual"


def test_update_and_delete_event(authenticated_client):
    event = authenticated_client.post(
        "/events",
        json={
            "title": "x",
            "start_at": "2026-09-10T14:00:00",
            "end_at": "2026-09-10T15:00:00",
        },
    ).json()

    response = authenticated_client.patch(f"/events/{event['id']}", json={"title": "y"})
    assert response.status_code == 200
    assert response.json()["title"] == "y"

    response = authenticated_client.delete(f"/events/{event['id']}")
    assert response.status_code == 204
    assert authenticated_client.get("/events").json() == []


# --- FASE 8: sobreposição de horário (MODULES/AGENDA.md, PLANNER.md) -------


def test_create_event_returns_409_on_overlap_without_creating(authenticated_client):
    authenticated_client.post(
        "/events",
        json={"title": "reunião", "start_at": "2026-09-10T14:00:00", "end_at": "2026-09-10T15:00:00"},
    )

    response = authenticated_client.post(
        "/events",
        json={
            "title": "outra",
            "start_at": "2026-09-10T14:30:00",
            "end_at": "2026-09-10T15:30:00",
        },
    )

    assert response.status_code == 409
    assert len(response.json()["detail"]["conflicting_events"]) == 1
    assert len(authenticated_client.get("/events").json()) == 1


def test_create_event_with_confirm_overlap_creates_despite_conflict(authenticated_client):
    authenticated_client.post(
        "/events",
        json={"title": "reunião", "start_at": "2026-09-10T14:00:00", "end_at": "2026-09-10T15:00:00"},
    )

    response = authenticated_client.post(
        "/events",
        json={
            "title": "outra",
            "start_at": "2026-09-10T14:30:00",
            "end_at": "2026-09-10T15:30:00",
            "confirm_overlap": True,
        },
    )

    assert response.status_code == 201
    assert len(authenticated_client.get("/events").json()) == 2


def test_update_event_returns_409_when_new_time_overlaps_another(authenticated_client):
    first = authenticated_client.post(
        "/events",
        json={"title": "reunião", "start_at": "2026-09-10T14:00:00", "end_at": "2026-09-10T15:00:00"},
    ).json()
    second = authenticated_client.post(
        "/events",
        json={"title": "livre", "start_at": "2026-09-10T16:00:00", "end_at": "2026-09-10T17:00:00"},
    ).json()

    response = authenticated_client.patch(
        f"/events/{second['id']}", json={"start_at": first["start_at"]}
    )

    assert response.status_code == 409
