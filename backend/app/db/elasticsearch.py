"""Elasticsearch async client factory.

Uses elasticsearch[async]. No connection is established at import time —
the client is created lazily and connects only when an API call is made.
"""

from __future__ import annotations

from elasticsearch import AsyncElasticsearch

from app.settings import settings

_client: AsyncElasticsearch | None = None


def get_elasticsearch() -> AsyncElasticsearch:
    """Return a configured async Elasticsearch client, creating it on first call."""
    global _client
    if _client is None:
        _client = AsyncElasticsearch(
            hosts=[settings.elasticsearch_url],
            # Do not log credentials — only the URL is used.
        )
    return _client


def reset_elasticsearch() -> None:
    """Reset cached Elasticsearch client (useful for tests)."""
    global _client
    _client = None
