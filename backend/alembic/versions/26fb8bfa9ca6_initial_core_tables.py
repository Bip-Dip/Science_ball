"""initial_core_tables

Revision ID: 26fb8bfa9ca6
Revises: 
Create Date: 2026-07-03 14:43:23.485489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26fb8bfa9ca6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── documents ───────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("access_level", sa.String(length=50), nullable=False),
        sa.Column("minio_bucket", sa.String(length=255), nullable=False),
        sa.Column("minio_object_key", sa.Text(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("created_by", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
    )
    op.create_index(
        op.f("ix_documents_access_level"),
        "documents",
        ["access_level"],
    )
    op.create_index(
        op.f("ix_documents_source_type"),
        "documents",
        ["source_type"],
    )

    # ── chunks ──────────────────────────────────────────────────────
    op.create_table(
        "chunks",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "document_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("section", sa.Text(), nullable=True),
        sa.Column("access_level", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chunks")),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_chunks_document_id_documents"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        op.f("ix_chunks_access_level"), "chunks", ["access_level"]
    )
    op.create_index(
        op.f("ix_chunks_document_id"), "chunks", ["document_id"]
    )

    # ── entities ────────────────────────────────────────────────────
    op.create_table(
        "entities",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "document_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "chunk_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("canonical_name", sa.Text(), nullable=True),
        sa.Column("aliases", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("extraction_method", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_entities")),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_entities_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["chunks.id"],
            name=op.f("fk_entities_chunk_id_chunks"),
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        op.f("ix_entities_document_id"), "entities", ["document_id"]
    )
    op.create_index(
        op.f("ix_entities_chunk_id"), "entities", ["chunk_id"]
    )
    op.create_index(
        op.f("ix_entities_entity_type"), "entities", ["entity_type"]
    )

    # ── facts ───────────────────────────────────────────────────────
    op.create_table(
        "facts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", sa.Text(), nullable=False),
        sa.Column("subject_type", sa.String(length=50), nullable=False),
        sa.Column("predicate", sa.String(length=100), nullable=False),
        sa.Column("object_id", sa.Text(), nullable=False),
        sa.Column("object_type", sa.String(length=50), nullable=False),
        sa.Column(
            "source_document_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "source_chunk_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "verification_status",
            sa.String(length=50),
            nullable=False,
            server_default="machine_extracted",
        ),
        sa.Column("extraction_method", sa.String(length=50), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("source_reliability", sa.Float(), nullable=True),
        sa.Column(
            "created_by", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_facts")),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["documents.id"],
            name=op.f("fk_facts_source_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_chunk_id"],
            ["chunks.id"],
            name=op.f("fk_facts_source_chunk_id_chunks"),
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        op.f("ix_facts_source_document_id"), "facts", ["source_document_id"]
    )
    op.create_index(
        op.f("ix_facts_source_chunk_id"), "facts", ["source_chunk_id"]
    )
    op.create_index(
        op.f("ix_facts_subject_type"), "facts", ["subject_type"]
    )
    op.create_index(
        op.f("ix_facts_predicate"), "facts", ["predicate"]
    )
    op.create_index(
        op.f("ix_facts_object_type"), "facts", ["object_type"]
    )
    op.create_index(
        op.f("ix_facts_verification_status"),
        "facts",
        ["verification_status"],
    )

    # ── fact_versions ───────────────────────────────────────────────
    op.create_table(
        "fact_versions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "fact_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column(
            "changed_by", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fact_versions")),
        sa.ForeignKeyConstraint(
            ["fact_id"],
            ["facts.id"],
            name=op.f("fk_fact_versions_fact_id_facts"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        op.f("ix_fact_versions_fact_id"), "fact_versions", ["fact_id"]
    )

    # ── ingestion_jobs ──────────────────────────────────────────────
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "document_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("progress", sa.Float(), nullable=True),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_by", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingestion_jobs")),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_ingestion_jobs_document_id_documents"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        op.f("ix_ingestion_jobs_document_id"),
        "ingestion_jobs",
        ["document_id"],
    )
    op.create_index(
        op.f("ix_ingestion_jobs_status"), "ingestion_jobs", ["status"]
    )

    # ── audit_log ───────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", sa.Text(), nullable=True),
        sa.Column("payload", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log")),
    )
    op.create_index(
        op.f("ix_audit_log_user_id"), "audit_log", ["user_id"]
    )
    op.create_index(
        op.f("ix_audit_log_action"), "audit_log", ["action"]
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("ingestion_jobs")
    op.drop_table("fact_versions")
    op.drop_table("facts")
    op.drop_table("entities")
    op.drop_table("chunks")
    op.drop_table("documents")
