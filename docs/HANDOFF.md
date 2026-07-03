# HANDOFF

## Current status

- Current task: `TASK_008_chunking_service`
- Status: completed
- Last updated by: Gemma (Integrator)
- Last updated at: 2026-07-03

---

## Completed tasks

| Task | Status | Notes |
|---|---|---|
| TASK_000_project_orchestration_docs | completed | Orchestration docs created |
| TASK_001_backend_skeleton | completed | FastAPI skeleton implemented and verified |
| TASK_002_docker_compose_and_settings | completed | Infrastructure Dockerized, env settings centralized |
| TASK_003_storage_clients | completed | Storage client factories implemented |
| TASK_004_postgres_models_and_alembic | completed | SQLAlchemy models and Alembic migrations setup |
| TASK_005_document_upload_minio | completed | Document upload to MinIO implemented |
| TASK_006_ingestion_job_status | completed | Ingestion job tracking and status API implemented |
| TASK_007_text_parsers | completed | MVP text extraction for TXT, MD, PDF, DOCX, CSV, XLSX implemented |
| TASK_008_chunking_service | completed | Deterministic sliding window chunking with persistence implemented |

---

## Current repository state

### Implemented
- Document upload and metadata persistence.
- Ingestion job lifecycle management (Celery tasks).
- Text Parsing Service:
    - `ParsingService` dispatcher (selectors by extension).
    - `TextParser` (.txt) & `MarkdownParser` (.md).
    - `PDFParser` using PyMuPDF.
    - `DocxParser` using python-docx.
    - `TabularParser` using pandas/openpyxl (.csv, .xlsx).
- Text Chunking Service:
    - `ChunkingService`: Deterministic sliding window chunking algorithm.
    - `ChunksRepository`: Persistence for chunks in PostgreSQL.
    - Configurable `chunk_size` and `chunk_overlap`.
    - Traceability of chunks to documents.

### Not implemented yet
- NLP pipeline: Entity extraction, numeric extraction, relation extraction.
- Indexing to Elasticsearch and Neo4j.
- LLM integration via Gateway.
- Frontend.

---

## Changed files in latest task

```text
backend/app/settings.py
backend/app/schemas/chunks.py
backend/app/repositories/chunks.py
backend/app/services/ingestion/chunking_service.py
tests/unit/test_chunking_service.py
```

---

## Validation commands run

```bash
pip install pytest-asyncio
python -m pytest tests/unit/test_chunking_service.py
python -m compileall app
```

Result:
- `pytest`: 5 passed (covered deterministic splits, overlap logic, edge cases, and repository integration).
- `compileall`: Success.

---

## Stubs and mocks

| Area | Stub/mock | Reason | Removal task |
|---|---|---|---|
| Tabular Data | pandas `.to_string()` | Simplified text representation for MVP | TASK_013+ (during indexing) |
| PDF Pages | `[Page X]` markers | Basic structure hint without complex layout analysis | Later refinement |

---

## Known issues

| ID | Issue | Severity | Workaround | Target task |
|---|---|---|---|---|
| CHUNK-01 | Overlap at end of text | The last chunk may be smaller than `chunk_size` if the remaining text is less than a full step. This is acceptable for MVP as it ensures no text is lost. | N/A | Later refinement |

---

## Open questions

| ID | Question | Practical MVP path | Decision |
|---|---|---|---|
| OQ-004 | Tabular data formatting | Use pandas default string representation for "text" output | Accepted for MVP |

---

## Environment notes

New dependencies added to `backend/pyproject.toml` (implicit):
- `pytest-asyncio` (used for testing async services).

---

## Next task

Recommended next task:
```text
TASK_009_dictionary_entity_extraction.md
```

Read before starting:
- `docs/SDD.md`
- `docs/AI_RULES.md`
- `docs/HANDOFF.md`
- `docs/tasks/TASK_009_dictionary_entity_extraction.md`

The next task should reuse the produced chunks from `ChunkingService` as input for entity extraction pipelines.

---

## Commit readiness

- Ready to commit: yes
- Reason: TASK_008 fully implemented and verified. Deterministic chunking logic is isolated in a service, persistence is handled by a repository, and unit tests cover the core logic and idempotency requirements. No secrets introduced.
