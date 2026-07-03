"""Tests for storage client factories.

All tests use construction-only validation or mocks — no live credentials
or external service connections are required.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


# ── PostgreSQL ──────────────────────────────────────────────────────────


class TestPostgresClient:
    """Tests for backend/app/db/postgres.py."""

    def test_get_engine_uses_settings_database_url(self):
        from app.db.postgres import reset_engine, get_engine

        reset_engine()
        with patch("app.db.postgres.create_async_engine") as mock_create:
            get_engine()
            mock_create.assert_called_once()
            args, kwargs = mock_create.call_args
            # First positional arg is the database URL from settings.
            assert "postgresql+asyncpg://" in args[0]

    def test_get_session_factory_returns_async_sessionmaker(self):
        from app.db.postgres import reset_engine, get_session_factory

        reset_engine()
        factory = get_session_factory()
        assert factory is not None
        # async_sessionmaker is callable to produce sessions.
        assert callable(factory)

    def test_reset_engine_clears_cache(self):
        from app.db.postgres import reset_engine, get_engine

        reset_engine()
        engine_a = get_engine()
        reset_engine()
        engine_b = get_engine()
        # After reset, a new engine should be created.
        assert engine_a is not engine_b


# ── Redis ───────────────────────────────────────────────────────────────


class TestRedisClient:
    """Tests for backend/app/db/redis.py."""

    def test_get_redis_uses_settings_redis_url(self):
        from app.db.redis import reset_redis, get_redis

        reset_redis()
        with patch("app.db.redis.aioredis.from_url") as mock_from_url:
            get_redis()
            mock_from_url.assert_called_once()
            args, kwargs = mock_from_url.call_args
            assert "redis://" in args[0]
            assert kwargs.get("decode_responses") is True

    def test_get_redis_returns_same_instance_on_repeated_calls(self):
        from app.db.redis import reset_redis, get_redis

        reset_redis()
        client_a = get_redis()
        client_b = get_redis()
        assert client_a is client_b

    def test_reset_redis_clears_cache(self):
        from app.db.redis import reset_redis, get_redis

        reset_redis()
        client_a = get_redis()
        reset_redis()
        client_b = get_redis()
        assert client_a is not client_b


# ── Elasticsearch ───────────────────────────────────────────────────────


class TestElasticsearchClient:
    """Tests for backend/app/db/elasticsearch.py."""

    def test_get_elasticsearch_uses_settings_url(self):
        from app.db.elasticsearch import reset_elasticsearch, get_elasticsearch

        reset_elasticsearch()
        with patch("app.db.elasticsearch.AsyncElasticsearch") as mock_es:
            get_elasticsearch()
            mock_es.assert_called_once()
            args, kwargs = mock_es.call_args
            hosts = kwargs.get("hosts", args[0] if args else [])
            assert any("localhost" in h for h in hosts)

    def test_get_elasticsearch_returns_same_instance_on_repeated_calls(self):
        from app.db.elasticsearch import reset_elasticsearch, get_elasticsearch

        reset_elasticsearch()
        client_a = get_elasticsearch()
        client_b = get_elasticsearch()
        assert client_a is client_b

    def test_reset_elasticsearch_clears_cache(self):
        from app.db.elasticsearch import reset_elasticsearch, get_elasticsearch

        reset_elasticsearch()
        client_a = get_elasticsearch()
        reset_elasticsearch()
        client_b = get_elasticsearch()
        assert client_a is not client_b


# ── Neo4j ───────────────────────────────────────────────────────────────


class TestNeo4jClient:
    """Tests for backend/app/db/neo4j.py."""

    def test_get_neo4j_driver_uses_settings_uri_and_auth(self):
        from app.db.neo4j import reset_neo4j_driver, get_neo4j_driver

        reset_neo4j_driver()
        with patch("app.db.neo4j.AsyncGraphDatabase.driver") as mock_driver:
            get_neo4j_driver()
            mock_driver.assert_called_once()
            args, kwargs = mock_driver.call_args
            assert "bolt://" in args[0]
            assert kwargs.get("auth") is not None

    def test_get_neo4j_driver_returns_same_instance_on_repeated_calls(self):
        from app.db.neo4j import reset_neo4j_driver, get_neo4j_driver

        reset_neo4j_driver()
        driver_a = get_neo4j_driver()
        driver_b = get_neo4j_driver()
        assert driver_a is driver_b

    def test_reset_neo4j_driver_clears_cache(self):
        from app.db.neo4j import reset_neo4j_driver, get_neo4j_driver

        reset_neo4j_driver()
        driver_a = get_neo4j_driver()
        reset_neo4j_driver()
        driver_b = get_neo4j_driver()
        assert driver_a is not driver_b


# ── MinIO ───────────────────────────────────────────────────────────────


class TestMinioClient:
    """Tests for backend/app/db/minio.py."""

    def test_get_minio_uses_settings_endpoint_and_credentials(self):
        from app.db.minio import reset_minio, get_minio

        reset_minio()
        with patch("app.db.minio.Minio") as mock_minio:
            get_minio()
            mock_minio.assert_called_once()
            args, kwargs = mock_minio.call_args
            assert kwargs.get("endpoint") == "localhost:9000"
            assert kwargs.get("access_key") == "minioadmin"
            # secret_key is passed but we don't assert its value in test output.
            assert "secret_key" in kwargs

    def test_get_minio_returns_same_instance_on_repeated_calls(self):
        from app.db.minio import reset_minio, get_minio

        reset_minio()
        client_a = get_minio()
        client_b = get_minio()
        assert client_a is client_b

    def test_reset_minio_clears_cache(self):
        from app.db.minio import reset_minio, get_minio

        reset_minio()
        client_a = get_minio()
        reset_minio()
        client_b = get_minio()
        assert client_a is not client_b


# ── Errors ──────────────────────────────────────────────────────────────


class TestStorageErrors:
    """Tests for backend/app/db/errors.py."""

    def test_storage_client_error_is_exception(self):
        from app.db.errors import StorageClientError

        with pytest.raises(StorageClientError):
            raise StorageClientError("test")

    def test_storage_client_config_error_inherits_base(self):
        from app.db.errors import StorageClientConfigError, StorageClientError

        assert issubclass(StorageClientConfigError, StorageClientError)


# ── Health config endpoint ──────────────────────────────────────────────


class TestHealthConfig:
    """Tests for /api/v1/health/config endpoint."""

    @pytest.fixture
    def anyio_backend(self) -> str:
        return "asyncio"

    @pytest.mark.anyio
    async def test_health_config_returns_storage_status(self):
        from httpx import ASGITransport, AsyncClient

        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health/config")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "storage_config" in data
        storage = data["storage_config"]
        assert storage["postgres"] == "configured"
        assert storage["redis"] == "configured"
        assert storage["elasticsearch"] == "configured"
        assert storage["neo4j"] == "configured"
        assert storage["minio"] == "configured"


# ── App import safety ───────────────────────────────────────────────────


def test_app_imports_without_live_services():
    """Verify that importing the app does not require live external services."""
    # This test passes simply by reaching this line — if any module
    # eagerly connected to an external service, the import would fail.
    from app.main import app  # noqa: F401
