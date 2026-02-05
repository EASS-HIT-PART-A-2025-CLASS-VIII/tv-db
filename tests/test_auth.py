from datetime import timedelta

from fastapi.testclient import TestClient

from app.models import UserDB
from app.security import create_access_token, hash_password


def _create_user(session, username: str, password: str, role: str) -> None:
    user = UserDB(username=username, hashed_password=hash_password(password), role=role)
    session.add(user)
    session.commit()


def test_login_success(client: TestClient, session):
    _create_user(session, "admin", "secret", "admin")
    response = client.post("/auth/login", json={"username": "admin", "password": "secret"})
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_admin_requires_token(client: TestClient):
    response = client.get("/admin/metrics")
    assert response.status_code == 401


def test_admin_rejects_insufficient_role(client: TestClient):
    token = create_access_token("viewer", "viewer")
    response = client.get(
        "/admin/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_expired_token_rejected(client: TestClient):
    token = create_access_token("admin", "admin", expires_delta=timedelta(seconds=-1))
    response = client.get(
        "/admin/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_register_creates_viewer(client: TestClient):
    response = client.post("/auth/register", json={"username": "newbie", "password": "pass"})
    assert response.status_code == 201
    login = client.post("/auth/login", json={"username": "newbie", "password": "pass"})
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_register_rejects_duplicate(client: TestClient):
    first = client.post("/auth/register", json={"username": "dup", "password": "pass"})
    assert first.status_code == 201
    second = client.post("/auth/register", json={"username": "dup", "password": "pass"})
    assert second.status_code == 409
