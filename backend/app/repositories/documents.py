"""Document repository — PostgreSQL operations for the documents table.

All methods receive an async SQLAlchemy session and do not manage
transactions directly — the caller (service) is responsible for commit/rollback.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentsRepository:
    async def create_document(
        self,
        session: AsyncSession,
        *,
        title: str,
        source_type: str,
        access_level: str,
        minio_bucket: str,
        minio_object_key: str,
        checksum: str,
        language: str | None = None,
        year: int | None = None,
        created_by: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
    ) -> Document:
        """Insert a new document row and return the model instance.

        The caller must commit the session after this call.
        """
        document = Document(
            id=document_id or uuid.uuid4(),
            title=title,
            source_type=source_type,
            access_level=access_level,
            minio_bucket=minio_bucket,
            minio_object_key=minio_object_key,
            checksum=checksum,
            language=language,
            year=year,
            created_by=created_by,
        )
        session.add(document)
        await session.flush()
        return document


    async def get_document_by_id(
        self,
        session: AsyncSession,
        document_id: uuid.UUID,
    ) -> Document | None:
        """Return a document by primary key, or None."""
        result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()
