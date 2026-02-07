from fastapi.testclient import TestClient

from app.models import UserDB
from app.security import hash_password


def _token_for(client: TestClient, session, username: str, password: str, role: str) -> str:
    session.add(UserDB(username=username, hashed_password=hash_password(password), role=role))
    session.commit()
    response = client.post("/auth/login", json={"username": username, "password": password})
    return response.json()["access_token"]


def test_ai_summary_uses_mocked_generator(client: TestClient, session, monkeypatch):
    from app.routes import ai as ai_routes
    from app.ai import SummaryResult

    async def _fake_summary(_):
        return SummaryResult(summary="ok", highlights=["one", "two"])

    monkeypatch.setattr(ai_routes, "generate_summary", _fake_summary)

    token = _token_for(client, session, "viewer", "viewer-pass", "viewer")
    response = client.post("/ai/summary", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == "ok"
    assert payload["highlights"] == ["one", "two"]
