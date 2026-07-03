"""Redis async client factory.

Uses redis.asyncio. No connection is established at import time —
the client is created lazily and connects only when a command is issued.
"""

from __future__ import annotations

import redis.asyncio as aioredis

from app.settings import settings

_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    """Return a configured async Redis client, creating it on first call."""
    global _client
    if _client is None:
        _client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _client


def reset_redis() -> None:
    """Reset cached Redis client (useful for tests)."""
    global _client
    _client = None
