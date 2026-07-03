# HANDOFF

## Current status

- Current task: `TASK_010_numeric_extractor_and_units`
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
| TASK_009_dictionary_entity_extraction | completed | Dictionary-based entity extraction (Material, Process, etc.) implemented |
| TASK_010_numeric_extractor_and_units | completed | Regex-based numeric extractor and SI unit normalizer implemented |

---

## Current repository state

### Implemented
- Document upload and metadata persistence.
- Ingestion job lifecycle management (Celery tasks).
- Text Parsing Service:
    - `ParsingService` dispatcher.
    - Support for TXT, MD, PDF, DOCX, CSV, XLSX.
- Text Chunking Service:
    - `ChunkingService`: Deterministic sliding window chunking.
    - `ChunksRepository`: Persistence in PostgreSQL.
- Entity Extraction Service (NLP MVP):
    - `EntityExtractor`: Deterministic matching using domain dictionaries and aliases.
    - `EntityExtractionService`: Orchestrates extraction for document chunks with idempotency.
    - `EntitiesRepository`: Persistence of extracted entities tied to documents and chunks.
    - Domain dictionary supporting Material, Process, Equipment, Property, Organization, Location.
- Numeric Extraction Service:
    - `NumericExtractor`: Deterministic regex-based extraction of technical parameters (Temp, pH, Pressure, etc.) in RU/EN.
    - `UnitNormalizer`: Normalizes extracted units to SI base units (e.g., Celsius $\rightarrow$ Kelvin).
    - `NumericCondition` model: Stores raw and normalized values with traceability to chunks.
    - `FactsRepository`: Handles persistence of numeric conditions and their links as Facts (`OPERATES_AT_CONDITION`).

### Not implemented yet
- Confidence scoring for facts.
- Indexing to Elasticsearch and Neo4j.
- LLM integration via Gateway.
- Frontend.

---

## Changed files in latest task

```text
backend/app/models/fact.py
backend/app/services/nlp/unit_normalizer.py
backend/app/services/nlp/numeric_extractor.py
backend/app/repositories/facts.py
backend/tests/unit/test_numeric_extractor.py
```

---

## Validation commands run

```bash
cd backend
python -m pytest tests/unit/test_numeric_extractor.py
python -m compileall app
```

Result:
- `pytest`: 7 passed (covered RU/EN extraction, comma decimals, SI normalization for temperature, pressure, and velocity).
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
| CHUNK-01 | Overlap at end of text | Last chunk may be smaller than `chunk_size`. | N/A | Later refinement |
| ENTITY-01 | Simple Dictionary Match | Only finds exact alias matches. | Acceptable for MVP dictionary phase. | Future NLP Refinement |
| NUMERIC-01 | Regex Simplicity | Complex phrasing or indirect numeric references are missed. | Deterministic regex is the requirement for MVP. | Future LLM-assisted refinement |

---

## Open questions

| ID | Question | Practical MVP path | Decision |
|---|---|---|---|
| OQ-004 | Tabular data formatting | Use pandas default string representation for "text" output | Accepted for MVP |

---

## Environment notes

No new external dependencies added. `pytest` used for validation.

---

## Next task

Recommended next task:
```text
TASK_011_confidence_service.md
```

Read before and reuse from this task:
- Reuse the extracted numeric conditions to calculate their contribution to fact confidence.
- The `FactsRepository` and `NumericCondition` model are ready for use in calculating evidence scores.
- Follow the formula defined in SDD (section 10) using extraction method and source reliability.

---

## Commit readiness

- Ready to commit: yes
- Reason: TASK_010 fully implemented and verified. Regex extraction handles RU/EN, units are normalized to SI, and persistence logic for candidate facts is provided. No secrets introduced.
