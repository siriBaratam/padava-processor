"""Redis client factory shared by agent modules."""

from __future__ import annotations

from typing import Any


def get_redis_client(redis_url: str) -> Any:
    """Create a Redis client with decoded string responses.

    The import stays inside this function so modules that only use the
    deterministic calculation layer can be tested without Redis installed.
    """
    import redis

    return redis.Redis.from_url(redis_url, decode_responses=True)
