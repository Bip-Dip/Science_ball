"""Tests for SQLAlchemy models — schema correctness, constraints, and defaults.

No live PostgreSQL connection is required — these tests validate
model definitions, column types, and relationship wiring.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB, UUID


# ── Model import safety ─────────────────────────────────────────────────


def test_all_models_importable():
    """All core models must be importable without a live database."""
    from app.models import (
        AuditLog,
        Base,
        Chunk,
        Document,
        Entity,
        Fact,
        FactVersion,
        IngestionJob,
        metadata,
    )

    assert Base is not None
    assert metadata is not None


# ── Metadata / naming convention ────────────────────────────────────────


class TestMetadata:
    def test_metadata_has_naming_convention(self):
        from app.models import metadata

        nc = metadata.naming_convention
        assert nc is not None
        assert nc["pk"] == "pk_%(table_name)s"
        assert nc["fk"] == "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
        assert nc["ix"] == "ix_%(column_0_label)s"

    def test_all_tables_registered_in_metadata(self):
        from app.models import metadata

        table_names = sorted(metadata.tables.keys())
        expected = [
            "audit_log",
            "chunks",
            "documents",
            "entities",
            "fact_versions",
            "facts",
            "ingestion_jobs",
        ]
        assert table_names == expected


# ── Document ────────────────────────────────────────────────────────────


class TestDocumentModel:
    def test_table_name(self):
        from app.models import Document

        assert Document.__tablename__ == "documents"

    def test_required_columns_present(self):
        from app.models import Document

        mapper = inspect(Document)
        col_names = {c.name for c in mapper.columns}
        required = {
            "id",
            "title",
            "source_type",
            "language",
            "year",
            "access_level",
            "minio_bucket",
            "minio_object_key",
            "checksum",
            "created_by",
            "created_at",
            "updated_at",
        }
        assert required.issubset(col_names)

    def test_id_is_uuid_pk(self):
        from app.models import Document

        col = inspect(Document).columns["id"]
        assert col.primary_key
        assert isinstance(col.type, UUID)

    def test_access_level_is_indexed(self):
        from app.models import Document

        col = inspect(Document).columns["access_level"]
        assert col.index is True

    def test_source_type_is_indexed(self):
        from app.models import Document

        col = inspect(Document).columns["source_type"]
        assert col.index is True

    def test_instantiate_minimal(self):
        from app.models import Document

        doc = Document(
            title="Test Document",
            source_type="publication",
            access_level="internal",
            minio_bucket="rd-documents",
            minio_object_key="test/doc.pdf",
            checksum="abc123",
        )
        assert doc.title == "Test Document"
        assert doc.access_level == "internal"
        # id is populated by the DB on INSERT; may be None before flush.
        assert doc.id is None or isinstance(doc.id, uuid.UUID)


# ── Chunk ───────────────────────────────────────────────────────────────


class TestChunkModel:
    def test_table_name(self):
        from app.models import Chunk

        assert Chunk.__tablename__ == "chunks"

    def test_required_columns_present(self):
        from app.models import Chunk

        mapper = inspect(Chunk)
        col_names = {c.name for c in mapper.columns}
        required = {
            "id",
            "document_id",
            "chunk_index",
            "text",
            "language",
            "page",
            "section",
            "access_level",
            "created_at",
        }
        assert required.issubset(col_names)

    def test_document_id_is_fk(self):
        from app.models import Chunk

        col = inspect(Chunk).columns["document_id"]
        assert len(col.foreign_keys) == 1
        fk = next(iter(col.foreign_keys))
        assert fk.column.table.name == "documents"

    def test_access_level_is_indexed(self):
        from app.models import Chunk

        col = inspect(Chunk).columns["access_level"]
        assert col.index is True

    def test_instantiate_minimal(self):
        from app.models import Chunk

        chunk = Chunk(
            document_id=uuid.uuid4(),
            chunk_index=0,
            text="Sample chunk text.",
            access_level="internal",
        )
        assert chunk.text == "Sample chunk text."
        assert chunk.chunk_index == 0
        # id is populated by the DB on INSERT; may be None before flush.
        assert chunk.id is None or isinstance(chunk.id, uuid.UUID)


# ── Entity ──────────────────────────────────────────────────────────────


class TestEntityModel:
    def test_table_name(self):
        from app.models import Entity

        assert Entity.__tablename__ == "entities"

    def test_required_columns_present(self):
        from app.models import Entity

        mapper = inspect(Entity)
        col_names = {c.name for c in mapper.columns}
        required = {
            "id",
            "document_id",
            "chunk_id",
            "entity_type",
            "name",
            "canonical_name",
            "aliases",
            "confidence",
            "extraction_method",
            "created_at",
        }
        assert required.issubset(col_names)

    def test_aliases_is_jsonb(self):
        from app.models import Entity

        col = inspect(Entity).columns["aliases"]
        assert isinstance(col.type, JSONB)

    def test_instantiate_minimal(self):
        from app.models import Entity

        entity = Entity(
            document_id=uuid.uuid4(),
            entity_type="Material",
            name="никель",
            confidence=0.9,
        )
        assert entity.entity_type == "Material"
        assert entity.name == "никель"


# ── Fact ────────────────────────────────────────────────────────────────


class TestFactModel:
    def test_table_name(self):
        from app.models import Fact

        assert Fact.__tablename__ == "facts"

    def test_required_columns_present(self):
        from app.models import Fact

        mapper = inspect(Fact)
        col_names = {c.name for c in mapper.columns}
        required = {
            "id",
            "subject_id",
            "subject_type",
            "predicate",
            "object_id",
            "object_type",
            "source_document_id",
            "source_chunk_id",
            "confidence",
            "verification_status",
            "extraction_method",
            "source_type",
            "source_reliability",
            "created_by",
            "created_at",
            "updated_at",
        }
        assert required.issubset(col_names)

    def test_source_document_id_is_fk(self):
        from app.models import Fact

        col = inspect(Fact).columns["source_document_id"]
        assert len(col.foreign_keys) == 1
        fk = next(iter(col.foreign_keys))
        assert fk.column.table.name == "documents"

    def test_source_chunk_id_is_fk(self):
        from app.models import Fact

        col = inspect(Fact).columns["source_chunk_id"]
        assert len(col.foreign_keys) == 1
        fk = next(iter(col.foreign_keys))
        assert fk.column.table.name == "chunks"

    def test_verification_status_default(self):
        from app.models import Fact

        col = inspect(Fact).columns["verification_status"]
        assert col.default is not None
        # The default is the string "machine_extracted"
        arg = col.default.arg
        assert arg == "machine_extracted"

    def test_instantiate_minimal(self):
        from app.models import Fact

        fact = Fact(
            subject_id="proc_electrowinning",
            subject_type="Process",
            predicate="OPERATES_AT_CONDITION",
            object_id="cond_123",
            object_type="Condition",
            source_document_id=uuid.uuid4(),
            confidence=0.84,
        )
        assert fact.predicate == "OPERATES_AT_CONDITION"
        assert fact.confidence == 0.84
        # verification_status default fires on INSERT; may be None before flush.
        assert fact.verification_status in (None, "machine_extracted")


# ── FactVersion ─────────────────────────────────────────────────────────


class TestFactVersionModel:
    def test_table_name(self):
        from app.models import FactVersion

        assert FactVersion.__tablename__ == "fact_versions"

    def test_fact_id_is_fk(self):
        from app.models import FactVersion

        col = inspect(FactVersion).columns["fact_id"]
        assert len(col.foreign_keys) == 1
        fk = next(iter(col.foreign_keys))
        assert fk.column.table.name == "facts"

    def test_payload_is_jsonb(self):
        from app.models import FactVersion

        col = inspect(FactVersion).columns["payload"]
        assert isinstance(col.type, JSONB)

    def test_instantiate_minimal(self):
        from app.models import FactVersion

        fv = FactVersion(
            fact_id=uuid.uuid4(),
            version=1,
            payload={"confidence": 0.9},
        )
        assert fv.version == 1
        assert fv.payload == {"confidence": 0.9}


# ── IngestionJob ────────────────────────────────────────────────────────


class TestIngestionJobModel:
    def test_table_name(self):
        from app.models import IngestionJob

        assert IngestionJob.__tablename__ == "ingestion_jobs"

    def test_document_id_is_fk(self):
        from app.models import IngestionJob

        col = inspect(IngestionJob).columns["document_id"]
        assert len(col.foreign_keys) == 1
        fk = next(iter(col.foreign_keys))
        assert fk.column.table.name == "documents"

    def test_status_default(self):
        from app.models import IngestionJob

        col = inspect(IngestionJob).columns["status"]
        assert col.default is not None
        assert col.default.arg == "pending"

    def test_instantiate_minimal(self):
        from app.models import IngestionJob

        job = IngestionJob(document_id=uuid.uuid4())
        # status default fires on INSERT; may be None before flush.
        assert job.status in (None, "pending")
        assert job.id is None or isinstance(job.id, uuid.UUID)


# ── AuditLog ────────────────────────────────────────────────────────────


class TestAuditLogModel:
    def test_table_name(self):
        from app.models import AuditLog

        assert AuditLog.__tablename__ == "audit_log"

    def test_required_columns_present(self):
        from app.models import AuditLog

        mapper = inspect(AuditLog)
        col_names = {c.name for c in mapper.columns}
        required = {
            "id",
            "user_id",
            "action",
            "entity_type",
            "entity_id",
            "payload",
            "created_at",
        }
        assert required.issubset(col_names)

    def test_payload_is_jsonb(self):
        from app.models import AuditLog

        col = inspect(AuditLog).columns["payload"]
        assert isinstance(col.type, JSONB)

    def test_instantiate_minimal(self):
        from app.models import AuditLog

        log = AuditLog(
            action="document_uploaded",
            entity_type="document",
            entity_id=str(uuid.uuid4()),
        )
        assert log.action == "document_uploaded"
        # id is populated by the DB on INSERT; may be None before flush.
        assert log.id is None or isinstance(log.id, uuid.UUID)


# ── Traceability / access_level contract ────────────────────────────────


class TestTraceabilityContract:
    """Verify that documents, chunks, and facts preserve traceability
    and access_level requirements per SDD."""

    def test_document_has_access_level(self):
        from app.models import Document

        assert "access_level" in {c.name for c in inspect(Document).columns}

    def test_chunk_has_access_level(self):
        from app.models import Chunk

        assert "access_level" in {c.name for c in inspect(Chunk).columns}

    def test_chunk_has_document_id_fk(self):
        from app.models import Chunk

        col = inspect(Chunk).columns["document_id"]
        assert len(col.foreign_keys) > 0

    def test_fact_has_source_document_id(self):
        from app.models import Fact

        assert "source_document_id" in {c.name for c in inspect(Fact).columns}

    def test_fact_has_source_chunk_id(self):
        from app.models import Fact

        assert "source_chunk_id" in {c.name for c in inspect(Fact).columns}

    def test_no_binary_columns_in_any_model(self):
        """No model should store binary files in PostgreSQL."""
        from sqlalchemy import LargeBinary

        from app.models import (
            AuditLog,
            Chunk,
            Document,
            Entity,
            Fact,
            FactVersion,
            IngestionJob,
        )

        for model in [Document, Chunk, Entity, Fact, FactVersion, IngestionJob, AuditLog]:
            for col in inspect(model).columns:
                assert not isinstance(col.type, LargeBinary), (
                    f"{model.__name__}.{col.name} is LargeBinary — "
                    f"binary files must not be stored in PostgreSQL"
                )
