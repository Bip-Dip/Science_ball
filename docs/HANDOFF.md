# HANDOFF

## Current status

- Current task: `TASK_007_text_parsers`
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
- Unit tests for all parsers covering happy paths and malformed files.

### Not implemented yet
- Text chunking logic (splitting documents into manageable pieces).
- NLP pipeline: Entity extraction, numeric extraction, relation extraction.
- Indexing to Elasticsearch and Neo4j.
- LLM integration via Gateway.
- Frontend.

---

## Changed files in latest task

```text
backend/pyproject.toml
backend/app/services/parsing/__init__.py
backend/app/services/parsing/base.py
backend/app/services/parsing/text_parser.py
backend/app/services/parsing/markdown_parser.py
backend/app/services/parsing/pdf_parser.py
backend/app/services/parsing/docx_parser.py
backend/app/services/parsing/tabular_parser.py
backend/tests/unit/test_text_parsers.py
```

---

## Validation commands run

```bash
cd backend
pip install pymupdf python-docx pandas openpyxl
python -m pytest tests/unit/test_text_parsers.py
python -m compileall app/services/parsing
```

Result:
- `pytest`: 9 passed (covered all supported extensions and error cases).
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
| PARSE-01 | Complex PDFs (multi-column) | Medium | PyMuPDF provides raw text; layout preservation is out of MVP scope | Future Refinement |

---

## Open questions

| ID | Question | Practical MVP path | Decision |
|---|---|---|---|
| OQ-004 | Tabular data formatting | Use pandas default string representation for "text" output | Accepted for MVP |

---

## Environment notes

New dependencies added to `backend/pyproject.toml`:
- `pymupdf`
- `python-docx`
- `pandas`
- `openpyxl`

---

## Next task

Recommended next task:
```text
TASK_008_chunking_service.md
```

Read before starting:
- `docs/SDD.md`
- `docs/AI_RULES.md`
- `docs/HANDOFF.md`
- `docs/tasks/TASK_008_chunking_service.md`

The next task should reuse the `ParsingService` to obtain raw text before applying chunking strategies.

---

## Commit readiness

- Ready to commit: yes
- Reason: TASK_007 fully implemented and verified. All supported formats (TXT, MD, PDF, DOCX, CSV, XLSX) are handled by a centralized dispatcher. Unit tests pass for all types. No secrets introduced.
