"""SQLAlchemy models for R&D Knowledge Map.

All models share the same declarative base and metadata so Alembic can
auto-generate migrations from `app.models.metadata`.
"""

from app.models.base import Base, metadata
from app.models.audit_log import AuditLog
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.entity import Entity
from app.models.fact import Fact, FactVersion
from app.models.ingestion_job import IngestionJob

__all__ = [
    "Base",
    "metadata",
    "AuditLog",
    "Chunk",
    "Document",
    "Entity",
    "Fact",
    "FactVersion",
    "IngestionJob",
]
