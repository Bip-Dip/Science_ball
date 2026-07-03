"""PostgreSQL async engine and session factory.

Uses SQLAlchemy 2.0 async style with asyncpg driver.
No connection is established at import time — the engine is created
lazily and sessions connect only when used.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _build_database_url() -> str:
    """Return the database URL from settings, with optional override."""
    return settings.database_url


def get_engine():
    """Return the async SQLAlchemy engine, creating it on first call."""
    global _engine
    if _engine is None:
        database_url = _build_database_url()
        _engine = create_async_engine(
            database_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the async session factory, creating it on first call."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


def reset_engine() -> None:
    """Reset cached engine and session factory (useful for tests)."""
    global _engine, _session_factory
    _engine = None
    _session_factory = None
