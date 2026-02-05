import asyncio
import json
import logging
import os
from datetime import datetime, timezone

import httpx
import redis.asyncio as redis

from .config import API_BASE_URL, REDIS_QUEUE, REDIS_URL

logger = logging.getLogger("tv_db.worker")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())


async def _login(client: httpx.AsyncClient, username: str, password: str) -> str:
    response = await client.post(
        f"{API_BASE_URL}/auth/login",
        json={"username": username, "password": password},
        timeout=5,
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("Worker login failed; access_token missing")
    return token


async def _build_report(client: httpx.AsyncClient) -> dict[str, str]:
    response = await client.get(f"{API_BASE_URL}/series", timeout=10)
    response.raise_for_status()
    series = response.json()
    total = len(series)
    avg_rating = None
    if total:
        ratings = [row["rating"] for row in series if row.get("rating") is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
    title = "Weekly TV Digest"
    content_lines = [
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"Total series: {total}",
        f"Average rating: {avg_rating:.2f}" if avg_rating is not None else "Average rating: n/a",
    ]
    return {"title": title, "content": "\n".join(content_lines)}


async def _handle_job(message: dict[str, str], client: httpx.AsyncClient, token: str) -> None:
    if message.get("job_type") != "report_digest":
        logger.warning("Unknown job type: %s", message.get("job_type"))
        return
    payload = await _build_report(client)
    response = await client.post(
        f"{API_BASE_URL}/reports",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    response.raise_for_status()
    logger.info("Report created for job %s", message.get("job_id"))


async def worker_loop() -> None:
    username = os.getenv("WORKER_USERNAME", "worker")
    password = os.getenv("WORKER_PASSWORD", "worker-pass")
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    async with httpx.AsyncClient() as client:
        token = await _login(client, username, password)
        while True:
            _, raw = await redis_client.blpop(REDIS_QUEUE)
            message = json.loads(raw)
            try:
                await _handle_job(message, client, token)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 401:
                    token = await _login(client, username, password)
                    await _handle_job(message, client, token)
                else:
                    logger.exception("Worker job failed: %s", exc)
            except Exception as exc:
                logger.exception("Worker job failed: %s", exc)


def main() -> None:
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
