from datetime import datetime, timezone
from typing import AsyncIterator
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel

from .config import REDIS_QUEUE, REDIS_URL


class QueueMessage(BaseModel):
    job_id: str
    job_type: str
    enqueued_at: str
    requested_by: str


async def get_redis() -> AsyncIterator[redis.Redis]:
    """Provide a Redis connection for async endpoints."""
    client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


async def enqueue_report_job(client: redis.Redis, requested_by: str) -> QueueMessage:
    """Push a report generation job to Redis."""
    message = QueueMessage(
        job_id=str(uuid4()),
        job_type="report_digest",
        enqueued_at=datetime.now(timezone.utc).isoformat(),
        requested_by=requested_by,
    )
    await client.rpush(REDIS_QUEUE, message.model_dump_json())
    return message
