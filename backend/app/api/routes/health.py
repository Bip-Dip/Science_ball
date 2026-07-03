"""Health check endpoints."""

from fastapi import APIRouter

from app.settings import settings

router = APIRouter()


def _build_config_status() -> dict[str, str]:
    """Return configuration status for each storage backend.

    Does NOT connect to external services — only checks that settings
    are present (non-empty URLs / endpoints).
    """
    return {
        "postgres": "configured" if settings.database_url else "missing",
        "redis": "configured" if settings.redis_url else "missing",
        "elasticsearch": "configured" if settings.elasticsearch_url else "missing",
        "neo4j": "configured" if settings.neo4j_uri else "missing",
        "minio": "configured" if settings.minio_endpoint else "missing",
    }


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
    }


@router.get("/api/v1/health")
async def health_v1() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0",
    }


@router.get("/api/v1/health/config")
async def health_config() -> dict[str, object]:
    """Return configuration status for all storage backends.

    This endpoint does NOT connect to external services.
    It only reports whether settings are present.
    """
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0",
        "storage_config": _build_config_status(),
    }
