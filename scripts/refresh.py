import asyncio
import os
from datetime import datetime, timezone
from typing import Any

import httpx
import redis.asyncio as redis

from app.config import API_BASE_URL, REDIS_URL


async def _with_retries(func, retries: int) -> Any:
    delay = 0.4
    for attempt in range(retries + 1):
        try:
            return await func()
        except Exception:
            if attempt >= retries:
                raise
            await asyncio.sleep(delay)
            delay *= 2


async def refresh_series(
    api_base: str,
    redis_client: redis.Redis,
    http_client: httpx.AsyncClient,
    concurrency: int = 5,
    retries: int = 2,
    trace_stream: str = "tvdb:refresh:trace",
) -> dict[str, int]:
    response = await http_client.get(f"{api_base}/series", timeout=10)
    response.raise_for_status()
    series_list = response.json()

    semaphore = asyncio.Semaphore(concurrency)
    today = datetime.now(timezone.utc).date().isoformat()
    stats = {"attempted": 0, "refreshed": 0, "skipped": 0, "failed": 0}

    async def _refresh_one(series_item: dict[str, Any]) -> None:
        series_id = series_item["id"]
        key = f"refresh:{series_id}:{today}"
        acquired = await redis_client.set(key, "1", ex=24 * 3600, nx=True)
        if not acquired:
            stats["skipped"] += 1
            return
        stats["attempted"] += 1

        async def _do_request():
            return await http_client.post(f"{api_base}/series/{series_id}/refresh", timeout=10)

        try:
            async with semaphore:
                response = await _with_retries(_do_request, retries)
            response.raise_for_status()
            stats["refreshed"] += 1
            await redis_client.xadd(
                trace_stream,
                {
                    "series_id": str(series_id),
                    "status": "refreshed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception:
            stats["failed"] += 1
            await redis_client.xadd(
                trace_stream,
                {
                    "series_id": str(series_id),
                    "status": "failed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

    await asyncio.gather(*[_refresh_one(item) for item in series_list])
    return stats


async def main() -> None:
    api_base = os.getenv("API_BASE_URL", API_BASE_URL)
    concurrency = int(os.getenv("REFRESH_CONCURRENCY", "5"))
    retries = int(os.getenv("REFRESH_RETRIES", "2"))

    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    async with httpx.AsyncClient() as http_client:
        stats = await refresh_series(
            api_base,
            redis_client,
            http_client,
            concurrency=concurrency,
            retries=retries,
        )
    await redis_client.close()
    print(f"Refresh complete: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
