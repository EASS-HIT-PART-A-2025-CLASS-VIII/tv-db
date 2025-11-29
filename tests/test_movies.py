from fastapi.testclient import TestClient


def test_get_movie_by_id(client: TestClient):
    payload = {"title": "Inception", "director": "Christopher Nolan", "year": 2010, "rating": 8.8}
    created = client.post("/movies", json=payload).json()

    response = client.get(f"/movies/{created['id']}")
    assert response.status_code == 200
    fetched = response.json()
    for key, value in payload.items():
        assert fetched[key] == value


def test_get_movie_not_found(client: TestClient):
    response = client.get("/movies/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Movie not found"
