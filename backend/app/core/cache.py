import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.redis import redis_client

RECENT_MESSAGES_LIMIT = 8


def _recent_key(conversation_id: UUID) -> str:
    return f"chat:{conversation_id}:recent_messages"


def _summary_key(conversation_id: UUID) -> str:
    return f"chat:{conversation_id}:summary"


def _quota_key(user_id: UUID) -> str:
    return f"user:{user_id}:quota"


async def get_recent_messages(conversation_id: UUID) -> list[dict[str, str]]:
    raw_items = await redis_client.lrange(_recent_key(conversation_id), 0, RECENT_MESSAGES_LIMIT - 1)
    return [json.loads(item) for item in raw_items]


async def set_recent_messages(conversation_id: UUID, messages: list[dict[str, str]]) -> None:
    key = _recent_key(conversation_id)
    await redis_client.delete(key)
    if messages:
        await redis_client.rpush(key, *[json.dumps(message) for message in messages[-RECENT_MESSAGES_LIMIT:]])
    await redis_client.expire(key, 60 * 60)


async def get_summary(conversation_id: UUID) -> str | None:
    return await redis_client.get(_summary_key(conversation_id))


async def set_summary(conversation_id: UUID, summary: str) -> None:
    await redis_client.set(_summary_key(conversation_id), summary, ex=60 * 60 * 24)


async def increment_daily_quota(user_id: UUID, tokens: int) -> int:
    key = _quota_key(user_id)
    total = await redis_client.incrby(key, tokens)
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    await redis_client.expireat(key, int(midnight.timestamp()))
    return total
