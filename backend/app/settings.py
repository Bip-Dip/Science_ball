"""Application settings loaded from environment variables.

Secrets must live only in `.env` and never be committed.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────
    app_name: str = "rd-knowledge-map-backend"
    debug: bool = False

    # ── PostgreSQL ───────────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://postgres:change_me@localhost:5432/rd_knowledge_map"
    )

    # ── Redis ────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Elasticsearch ────────────────────────────────────────────────
    elasticsearch_url: str = "http://localhost:9200"

    # ── Neo4j ────────────────────────────────────────────────────────
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "change_me"

    # ── MinIO ────────────────────────────────────────────────────────
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "change_me"
    minio_bucket: str = "rd-documents"
    minio_secure: bool = False

    # ── LLM Provider ─────────────────────────────────────────────────
    llm_provider: str = "mock"

    # ── YandexGPT ────────────────────────────────────────────────────
    yandex_api_key: str = "change_me"
    yandex_folder_id: str = "change_me"
    yandex_llm_model: str = "yandexgpt-lite"
    yandex_llm_model_version: str = "latest"
    yandex_llm_endpoint: str = (
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    )
    yandex_embeddings_enabled: bool = False
    yandex_embedding_query_model: str = "text-search-query"
    yandex_embedding_doc_model: str = "text-search-doc"
    yandex_embedding_endpoint: str = (
        "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"
    )

    # ── LLM common ───────────────────────────────────────────────────
    llm_temperature: float = 0.2
    llm_max_tokens: int = 3000
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 2

    # ── Chunking ───────────────────────────────────────────────────────
    chunk_size: int = 1000
    chunk_overlap: int = 200


    # ── Local LLM fallback ───────────────────────────────────────────
    local_llm_endpoint: str = "http://ollama:11434"
    local_llm_model: str = "qwen2.5:7b-instruct"


settings = Settings()
