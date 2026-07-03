# HANDOFF

## Current status

- Current task: `TASK_003_storage_clients`
- Status: completed
- Last updated by: Gemma (Integrator)
- Last updated at: 2026-07-03

---

## Completed tasks

| Task | Status | Commit | Notes |
|---|---|---|---|
| TASK_000_project_orchestration_docs | completed | TBD | Orchestration docs created |
| TASK_001_backend_skeleton | completed | TBD | FastAPI skeleton implemented and verified |
| TASK_002_docker_compose_and_settings | completed | TBD | Infrastructure Dockerized, env settings centralized |
| TASK_003_storage_clients | completed | TBD | Storage client factories implemented |

---

## Current repository state

### Implemented
- Orchestration documentation and task list.
- SDD copied to `docs/SDD.md`.
- Minimal FastAPI backend skeleton (app factory, health endpoints).
- Full MVP infrastructure in `docker-compose.yml` (Postgres, Redis, ES, Neo4j, MinIO).
- Backend Dockerfile with multi-stage build and non-root user.
- Centralized settings model reading from environment variables.
- Storage client factories for all backends:
    - PostgreSQL (SQLAlchemy 2.0 Async)
    - Redis (asyncio)
    - Elasticsearch (AsyncElasticsearch)
    - Neo4j (AsyncDriver)
    - MinIO (minio-py)
- Basic unit tests for storage clients using mocks.

### Not implemented yet
- PostgreSQL models and Alembic migrations.
- Document upload logic.
- Ingestion pipeline tasks.
- NLP/search/graph/LLM business logic.
- Frontend.

---

## Changed files in latest task

```text
backend/pyproject.toml
backend/app/api/routes/health.py
backend/app/db/__init__.py
backend/app/db/errors.py
backend/app/db/postgres.py
backend/app/db/redis.py
backend/app/db/elasticsearch.py
backend/app/db/neo4j.py
backend/app/db/minio.py
backend/app/worker/celery_app.py
backend/tests/unit/test_storage_clients.py
```

---

## Validation commands run

```bash
cd backend && python -m pytest
cd backend && python -m compileall app
```

Result:
```text
pytest: 21 passed (including all storage client tests)
compileall: Success (no errors)
```

---

## Storage Clients & Dependencies

### Client Modules
- `app.db.postgres`: Async engine and session factory.
- `app.db.redis`: Async Redis client.
- `app.db.elasticsearch`: Async ES client.
- `app.db.neo4j`: Async Neo4j driver.
- `app.db.minio`: MinIO client.
- `app.db.errors`: Base storage exceptions.

### Added Dependencies
- `sqlalchemy[asyncio]`, `asyncpg` (Postgres)
- `elasticsearch[async]` (Elasticsearch)
- `neo4j` (Neo4j)
- `minio` (MinIO)

---

## Stubs and mocks

| Area | Stub/mock | Reason | Removal task |
|---|---|---|---|
| Dependencies | `backend/app/dependencies.py` is empty | Skeleton phase; real deps in later tasks | TASK_004+ |
| Worker | `worker` service in compose | Placeholder for Celery runtime; no tasks yet | TASK_005+ |
| Storage | Client factories are lazy | No live connections required to import app | N/A (by design) |

---

## Known issues

| ID | Issue | Severity | Workaround | Target task |
|---|---|---|---|---|
| NONE | - | - | - | - |

---

## Open questions

| ID | Question | Practical MVP path | Decision |
|---|---|---|---|
| OQ-001 | SDD contains duplicated/garbled fragments in some sections. | Treat clean bullet lists and code blocks as intended source. Do not edit SDD. | Pending |
| OQ-002 | Exact upload size limits are not specified. | Use conservative configurable defaults in settings. | Pending |
| OQ-003 | Auth/RBAC depth for early MVP is not fully specified. | Start with `access_level` fields and later add real auth/RBAC. | Pending |

---

## Environment notes

Required local secrets must live only in `.env`.

Never commit:
- `.env`;
- real Yandex API key;
- real database passwords;
- real MinIO/Neo4j credentials.

---

## Next task

Recommended next task:

```text
TASK_004_postgres_models_and_alembic.md
```

Read before starting:
- `docs/SDD.md`
- `docs/AI_RULES.md`
- `docs/HANDOFF.md`
- `docs/tasks/TASK_004_postgres_models_and_alembic.md`

---

## Commit readiness

- Ready to commit: yes
- Reason: TASK_003 fully implemented and verified. Clients are lazy, tests pass using mocks, no secrets hardcoded, boundaries respected.
- Required before commit: none
