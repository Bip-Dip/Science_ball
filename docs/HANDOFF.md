# HANDOFF

## Current status

- Current task: `TASK_004_postgres_models_and_alembic`
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
| TASK_004_postgres_models_and_alembic | completed | TBD | SQLAlchemy models and Alembic migrations setup |

---

## Current repository state

### Implemented
- Orchestration documentation and task list.
- SDD copied to `docs/SDD.md`.
- Minimal FastAPI backend skeleton (app factory, health endpoints).
- Full MVP infrastructure in `docker-compose.yml` (Postgres, Redis, ES, Neo4j, MinIO).
- Backend Dockerfile with multi-stage build and non-root user.
- Centralized settings model reading from environment variables.
- Storage client factories for all backends (Lazy loading).
- SQLAlchemy 2.0 Core Models for MVP:
    - `documents` (access_level, MinIO links)
    - `chunks` (traceability, access_level)
    - `entities` (extracted entities, aliases)
    - `facts` & `fact_versions` (knowledge units, traceability, confidence)
    - `ingestion_jobs` (pipeline tracking)
    - `audit_log` (immutable audit trail)
- Alembic migration framework configured with initial revision.

### Not implemented yet
- Document upload logic and MinIO integration.
- Ingestion pipeline implementation.
- NLP/search/graph/LLM business logic.
- Frontend.

---

## Changed files in latest task

```text
backend/pyproject.toml
backend/alembic.ini
backend/alembic/env.py
backend/alembic/script.py.mako
backend/alembic/versions/26fb8bfa9ca6_initial_core_tables.py
backend/app/models/__init__.py
backend/app/models/base.py
backend/app/models/document.py
backend/app/models/chunk.py
backend/app/models/entity.py
backend/app/models/fact.py
backend/app/models/ingestion_job.py
backend/app/models/audit_log.py
backend/tests/unit/test_models.py
```

---

## Validation commands run

```bash
cd backend && python -m pytest
cd backend && python -m compileall app
```

Result:
```text
pytest: 63 passed (including model and migration tests)
compileall: Success (no errors)
```

---

## Database Schema & Migrations

### Migration Revision
- ID: `26fb8bfa9ca6`
- Title: `initial_core_tables`

### Tables Created
- `documents`: Metadata, checksums and access levels.
- `chunks`: Document segments with traceability.
- `entities`: Extracted named entities.
- `facts`: Knowledge units with confidence and source tracing.
- `fact_versions`: Versioning for facts via JSONB payload.
- `ingestion_jobs`: Tracking of ingestion pipeline state.
- `audit_log`: Immutable user action log.

---

## Stubs and mocks

| Area | Stub/mock | Reason | Removal task |
|---|---|---|---|
| Dependencies | `backend/app/dependencies.py` is empty | Skeleton phase; real deps in later tasks | TASK_005+ |
| Worker | `worker` service in compose | Placeholder for Celery runtime; no tasks yet | TASK_005+ |
| RBAC | user_id / created_by fields | Nullable UUIDs without FK (Users table pending) | Task: Auth/RBAC implementation |

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
| OQ-003 | Auth/RBAC depth for early MVP is not specified. | Start with `access_level` fields and later add real auth/RBAC. | Pending |

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
TASK_005_document_upload_minio.md
```

Read before starting:
- `docs/SDD.md`
- `docs/AI_RULES.md`
- `docs/HANDOFF.md`
- `docs/tasks/TASK_005_document_upload_minio.md`

---

## Commit readiness

- Ready to commit: yes
- Reason: TASK_004 fully implemented and verified. Models strictly follow SDD requirements (traceability, access levels). Alembic is configured and initial migration is present. No business logic leaked.
- Required before commit: none
