"""Neo4j async driver factory.

Uses neo4j AsyncDriver. No connection is established at import time —
the driver is created lazily and sessions connect only when used.
"""

from __future__ import annotations

from neo4j import AsyncGraphDatabase

from app.settings import settings

_driver = None


def get_neo4j_driver():
    """Return a configured async Neo4j driver, creating it on first call."""
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            # Do not log auth credentials.
        )
    return _driver


def reset_neo4j_driver() -> None:
    """Reset cached Neo4j driver (useful for tests)."""
    global _driver
    _driver = None
