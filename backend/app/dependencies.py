"""Shared FastAPI dependencies.

Provides dependency callables for FastAPI's Depends() injection.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.minio import get_minio
from app.db.postgres import get_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session and close it after the request."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_minio_client() -> Minio:
    """Return the MinIO client instance.

    Minio client is synchronous, so no async context manager is needed.
    """
    return get_minio()


async def get_current_user() -> str:
    """Return a dummy current user for MVP."""
    return "mvp_user"


async def get_ingestion_service() -> "IngestionJobService":
    """Provide the IngestionJobService with with its required repository."""
    from app.repositories.ingestion_jobs import IngestionJobRepository
    from app.services.ingestion.job_service import IngestionJobService

    return IngestionJobService(repository=IngestionJobRepository())

