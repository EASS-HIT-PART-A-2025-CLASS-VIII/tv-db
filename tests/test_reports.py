from fastapi.testclient import TestClient

from app.models import UserDB
from app.security import hash_password


def _token_for(client: TestClient, session, username: str, password: str, role: str) -> str:
    session.add(UserDB(username=username, hashed_password=hash_password(password), role=role))
    session.commit()
    response = client.post("/auth/login", json={"username": username, "password": password})
    return response.json()["access_token"]


def test_create_report_requires_admin_or_worker(client: TestClient, session):
    token = _token_for(client, session, "admin", "secret", "admin")
    response = client.post(
        "/reports",
        json={"title": "Digest", "content": "Hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Digest"
    assert body["created_by"] == "admin"


def test_list_reports_requires_admin(client: TestClient, session):
    token = _token_for(client, session, "admin", "secret", "admin")
    response = client.get("/reports", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
