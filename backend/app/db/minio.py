"""MinIO client factory.

Uses minio-py. No connection is established at import time —
the client is created lazily and connects only when an API call is made.
"""

from __future__ import annotations

from minio import Minio

from app.settings import settings

_client: Minio | None = None


def get_minio() -> Minio:
    """Return a configured MinIO client, creating it on first call."""
    global _client
    if _client is None:
        _client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
    return _client


def reset_minio() -> None:
    """Reset cached MinIO client (useful for tests)."""
    global _client
    _client = None
