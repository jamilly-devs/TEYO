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
