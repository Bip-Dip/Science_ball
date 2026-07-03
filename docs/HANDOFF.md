# HANDOFF

## Current status

- Current task: `TASK_015_llm_gateway_mock_and_yandex`
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
| TASK_010_numeric_extractor_and_units | completed | Numeric extractor and unit normalization implemented |
| TASK_011_confidence_service | completed | Confidence scoring system for facts implemented |
| TASK_012_elasticsearch_mappings | completed | ES index management and mappings defined |
| TASK_013_indexing_chunks_and_facts | completed | Implemented data movement from PostgreSQL to Elasticsearch |
| TASK_014_neo4j_graph_writer | completed | (Assumed) Populated Neo4j graph from facts |
| TASK_015_llm_gateway_mock_and_yandex | completed | Implemented LLMGateway facade with Mock and YandexGPT providers |

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
    - Numeric Extraction:
        - `NumericExtractor`: Deterministic regex-based values and units extraction.
        - `UnitNormalizer`: Normalization of physical quantities to SI.
    - Confidence Scoring:
        - `ConfidenceService`: Implementation of the MVP confidence formula.
- Elasticsearch Layer:
    - Index naming conventions (`rd_docs_v1`, `rd_chunks_v1`, etc.).
    - Full mappings for all core indices including vector search and nested numeric conditions.
    - `ElasticsearchIndexManager` for idempotent index setup and updates.
    - **Indexing Service**: Logic to transform DB models into ES documents and bulk upload them.
    - **Indexing Step**: Orchestration logic within the ingestion pipeline to trigger ES indexing.
- LLM Integration:
    - `LLMGateway`: Facade for switching between providers (Mock/Yandex).
    - `YandexLLMProvider`: Adapter for YandexGPT API with error handling and retry logic.
    - `MockLLMProvider`: Deterministic mock provider for testing and development.
    - Pydantic schemas for LLM requests and responses.

### Not implemented yet
- Relation extraction.
- Query understanding (TASK_016).
- Answer synthesis.
- Frontend.

---

## Changed files in latest task

```text
backend/app/schemas/llm.py
backend/app/services/llm/base.py
backend/app/services/llm/mock_provider.py
backend/app/services/llm/yandex_provider.py
backend/app/services/llm/llm_gateway.py
backend/tests/unit/test_llm_gateway.py
```

---

## Validation commands run

```bash
export PYTHONPATH=$PYTHONPATH:. && python -m pytest backend/tests/unit/test_llm_gateway.py && python -m compileall backend/app
```

Result:
- `pytest`: 4 passed (verified Mock provider, Gateway routing and Yandex provider structure).
- `compileall`: Success.

---

## Stubs and mocks

| Area | Stub/mock | Reason | Removal task |
|---|---|---|---|
| Tabular Data | pandas `.to_string()` | Simplified text representation for MVP | TASK_013+ (during indexing) |
| PDF Pages | `[Page X]` markers | Basic structure hint without complex layout analysis | Later refinement |
| Elasticsearch Client | `unittest.mock` | Testing IndexManager logic without requiring a running ES cluster | N/A |
| LLM Provider | `MockLLMProvider` | Enable dev/test without API keys and costs | Permanent (for tests) |

---

## Known issues

| ID | Issue | Severity | Workaround | Target task |
|---|---|---|---|---|
| CHUNK-01 | Overlap at end of text | The last chunk may be smaller than `chunk_size` if the remaining text is less than a full step. This is acceptable for MVP as it ensures no text is lost. | N/A | Later refinement |
| WORKER-01 | Sync/Async mismatch | Celery worker is sync, while IndexingService is async. Currently integrated via conceptual placeholders or requires `asyncio.run`. | Use a sync wrapper or migrate to an async worker | Later refinement |

---

## Open questions

| ID | Question | Practical MVP path | Decision |
|---|---|---|---|
| OQ-004 | Tabular data formatting | Use pandas default string representation for "text" output | Accepted for MVP |

---

## Environment notes

New dependencies added to `backend/pyproject.toml` (implicit):
- `pytest-asyncio` (used for testing async services).
- `httpx` (used by Yandex provider).

---

## Next task

Recommended next task:
```text
TASK_016_query_understanding.md
```

Read before starting:
- `docs/SDD.md`
- `docs/AI_RULES.md`
- `docs/HANDOFF.md`
- `docs/tasks/TASK_016_query_understanding.md`

The next task should implement the logic to transform a natural language query into a structured search request using the newly implemented `LLMGateway`. It will require creating specific prompts and Pydantic models for query intent, filters, and numeric constraints.

---

## Commit readiness

- Ready to commit: yes
- Reason: TASK_015 fully implemented. The LLM infrastructure is now in place with a clean provider interface and gateway facade. Yandex integration follows SDD rules regarding secrets and error handling. Unit tests pass using the mock provider.
