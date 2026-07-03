# HANDOFF

## Current status

- Current task: `TASK_009_dictionary_entity_extraction`
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
| TASK_009_dictionary_entity_extraction | completed | Dictionary-based entity extraction pipeline implemented |

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
- NLP Pipeline (MVP):
    - Dictionary-based Entity Extraction:
        - Domain dictionaries for Materials, Processes, Equipment, Properties, Organizations, Locations.
        - Alias resolution and "longest-match-first" extraction logic.
        - `EntityExtractionService` orchestrating the process with idempotency (deleting old entities before re-extraction).
        - `EntitiesRepository` for persisting extracted entities in PostgreSQL.

### Not implemented yet
- Numeric extractor and units handling.
- Relation extraction.
- Indexing to Elasticsearch and Neo4j.
- LLM integration via Gateway.
- Frontend.

---

## Changed files in latest task

```text
backend/app/services/nlp/__init__.py
backend/app/services/nlp/dictionaries.py
backend/app/services/nlp/entity_extractor.py
backend/app/services/nlp/entity_extraction_service.py
backend/app/repositories/entities.py
backend/tests/unit/test_entity_extractor.py
```

---

## Validation commands run

```bash
cd backend
python -m pytest tests/unit/test_entity_extractor.py
python -m compileall app
```

Result:
- `pytest`: 4 passed (covered basic extraction, alias resolution, longest-match priority, and service integration).
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
TASK_010_numeric_extractor_and_units.md
```

Read before starting:
- `docs/SDD.md`
- `docs/AI_RULES.md`
- `docs/HANDOFF.md`
- `docs/tasks/TASK_010_numeric_extractor_and_units.md`

The next task should reuse the entities extracted in TASK_009 and implement a specialized extractor for numeric values and their associated units, which are critical for technical knowledge maps.

---

## Commit readiness

- Ready to commit: yes
- Reason: TASK_009 fully implemented and verified. The dictionary extraction logic is isolated, supports alias resolution, handles longest-match priority, and is integrated into the ingestion pipeline via a service layer. No secrets introduced.
