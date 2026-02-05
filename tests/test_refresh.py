import fakeredis.aioredis
import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session

from app.db import get_session
from app.main import app
from app.models import SeriesDB
from scripts.refresh import refresh_series


@pytest.mark.anyio
async def test_refresh_series_idempotent(engine):
    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    with Session(engine) as session:
        session.add(
            SeriesDB(title="Andor", creator="Tony Gilroy", year=2022, rating=8.4),
        )
        session.commit()

    redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        first = await refresh_series("http://test", redis_client, ac, concurrency=2, retries=0)
        second = await refresh_series("http://test", redis_client, ac, concurrency=2, retries=0)

    app.dependency_overrides.clear()
    assert first["refreshed"] == 1
    assert second["refreshed"] == 0
    assert second["skipped"] == 1
