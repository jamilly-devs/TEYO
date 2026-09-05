def test_add_and_list_market_item(authenticated_client):
    response = authenticated_client.post(
        "/market/items", json={"name": "arroz", "category": "hortifruti"}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "active"

    response = authenticated_client.get("/market")
    assert len(response.json()) == 1


def test_patch_market_item_only_accepts_status(authenticated_client):
    item = authenticated_client.post("/market/items", json={"name": "arroz"}).json()

    response = authenticated_client.patch(
        f"/market/items/{item['id']}", json={"status": "purchased"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "purchased"
    # marking as purchased does not remove the row
    assert len(authenticated_client.get("/market").json()) == 1


def test_delete_market_item_removes_it_from_the_database(authenticated_client):
    item = authenticated_client.post("/market/items", json={"name": "arroz"}).json()
    response = authenticated_client.delete(f"/market/items/{item['id']}")
    assert response.status_code == 204
    assert authenticated_client.get("/market").json() == []
