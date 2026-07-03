"""Fact and FactVersion models.

Facts are the core knowledge unit — each fact traces back to a source
document and optionally a specific chunk.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class NumericCondition(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "numeric_conditions"

    property: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value_si: Mapped[float | None] = mapped_column(Float)
    normalized_unit_si: Mapped[str | None] = mapped_column(String(50))
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="SET NULL"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class Fact(Base, UUIDPrimaryKeyMixin):

    __tablename__ = "facts"

    subject_id: Mapped[str] = mapped_column(Text, nullable=False)
    subject_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    predicate: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    object_id: Mapped[str] = mapped_column(Text, nullable=False)
    object_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="SET NULL"),
        index=True,
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    verification_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="machine_extracted", index=True
    )
    extraction_method: Mapped[str | None] = mapped_column(String(50))
    source_type: Mapped[str | None] = mapped_column(String(50))
    source_reliability: Mapped[float | None] = mapped_column(Float)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class FactVersion(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "fact_versions"

    fact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    changed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    change_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
