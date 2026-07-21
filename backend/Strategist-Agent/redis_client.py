"""Redis client factory for the standalone Strategist-Agent folder."""

from __future__ import annotations

from typing import Any


def get_redis_client(redis_url: str) -> Any:
    """Create a Redis client with decoded string responses."""
    import redis

    return redis.Redis.from_url(redis_url, decode_responses=True)
