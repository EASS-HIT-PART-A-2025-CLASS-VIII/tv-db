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


def test_delete_series(client: TestClient):
    payload = {"title": "Dark", "creator": "Baran bo Odar", "year": 2017, "rating": 8.8}
    created = client.post("/series", json=payload).json()

    delete_response = client.delete(f"/series/{created['id']}")
    assert delete_response.status_code == 204

    list_response = client.get("/series")
    assert list_response.status_code == 200
    assert list_response.json() == []
