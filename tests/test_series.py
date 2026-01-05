from fastapi.testclient import TestClient


def test_list_series_initially_empty(client: TestClient):
    response = client.get("/series")
    assert response.status_code == 200
    assert response.json() == []


def test_create_series(client: TestClient):
    payload = {"title": "The Bear", "creator": "Christopher Storer", "year": 2022, "rating": 8.6}
    response = client.post("/series", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    for key, value in payload.items():
        assert body[key] == value


def test_get_series_by_id(client: TestClient):
    payload = {"title": "Mr. Robot", "creator": "Sam Esmail", "year": 2015, "rating": 8.5}
    created = client.post("/series", json=payload).json()

    response = client.get(f"/series/{created['id']}")
    assert response.status_code == 200
    fetched = response.json()
    for key, value in payload.items():
        assert fetched[key] == value


def test_get_series_returns_404_for_missing_id(client: TestClient):
    response = client.get("/series/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Series not found"


def test_put_series_updates_entry(client: TestClient):
    payload = {"title": "Severance", "creator": "Dan Erickson", "year": 2022, "rating": 8.7}
    created = client.post("/series", json=payload).json()

    update = {"title": "Severance", "creator": "Dan Erickson", "year": 2025, "rating": 9.0}
    response = client.put(f"/series/{created['id']}", json=update)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["year"] == update["year"]
    assert body["rating"] == update["rating"]


def test_put_series_returns_404_for_missing_id(client: TestClient):
    payload = {"title": "Andor", "creator": "Tony Gilroy", "year": 2022, "rating": 8.4}
    response = client.put("/series/999", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Series not found"


def test_patch_series_updates_entry(client: TestClient):
    payload = {"title": "Blue Eye Samurai", "creator": "Michael Green", "year": 2023, "rating": 8.7}
    created = client.post("/series", json=payload).json()

    response = client.patch(f"/series/{created['id']}", json={"rating": 9.1})
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["rating"] == 9.1


def test_patch_series_returns_404_for_missing_id(client: TestClient):
    response = client.patch("/series/999", json={"rating": 7.0})
    assert response.status_code == 404
    assert response.json()["detail"] == "Series not found"


def test_delete_series(client: TestClient):
    payload = {"title": "Dark", "creator": "Baran bo Odar", "year": 2017, "rating": 8.8}
    created = client.post("/series", json=payload).json()

    delete_response = client.delete(f"/series/{created['id']}")
    assert delete_response.status_code == 204

    list_response = client.get("/series")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_delete_series_returns_404_for_missing_id(client: TestClient):
    response = client.delete("/series/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Series not found"


def test_create_series_returns_existing_on_duplicate_payload(client: TestClient):
    payload = {"title": "The Bear", "creator": "Christopher Storer", "year": 2022, "rating": 8.6}
    first = client.post("/series", json=payload)
    assert first.status_code == 201
    first_body = first.json()

    second = client.post("/series", json=payload)
    assert second.status_code == 201
    second_body = second.json()

    assert first_body["id"] == second_body["id"]
    assert second_body["title"] == payload["title"]


def test_create_series_rejects_empty_title(client: TestClient):
    payload = {"title": "", "creator": "Somebody", "year": 2022, "rating": 7.0}
    response = client.post("/series", json=payload)
    assert response.status_code == 422


def test_create_series_rejects_rating_out_of_range(client: TestClient):
    payload = {"title": "Show", "creator": "Author", "year": 2022, "rating": 11}
    response = client.post("/series", json=payload)
    assert response.status_code == 422
