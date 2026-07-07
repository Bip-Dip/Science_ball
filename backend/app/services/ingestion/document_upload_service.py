"""Document upload service.

Orchestrates the MVP upload flow:
1. validate file extension
2. calculate checksum
3. upload original file to MinIO
4. persist metadata in PostgreSQL via repository
5. return DocumentResponse

Parsing, chunking, and Celery ingestion are NOT part of this service.
"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.documents import DocumentsRepository
from app.schemas.documents import MVP_ALLOWED_EXTENSIONS, DocumentResponse
from app.settings import settings


def _validate_extension(filename: str) -> str:
    """Return normalized lower-cased extension or raise ValueError."""
    ext = Path(filename).suffix.lower()
    if ext not in MVP_ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Allowed: {', '.join(sorted(MVP_ALLOWED_EXTENSIONS))}"
        )
    return ext


def _calculate_checksum(file_bytes: bytes) -> str:
    """Return SHA-256 hex digest of file contents."""
    return hashlib.sha256(file_bytes).hexdigest()


def _build_object_key(document_id: uuid.UUID, extension: str) -> str:
    """Build a deterministic MinIO object key to avoid collisions."""
    return f"documents/{document_id}/{document_id}{extension}"


async def upload_document(
    session: AsyncSession,
    minio_client: Minio,
    *,
    file_bytes: bytes,
    filename: str,
    content_type: str,
    title: str,
    source_type: str,
    access_level: str,
    language: str | None = None,
    year: int | None = None,
    created_by: uuid.UUID | None = None,
) -> DocumentResponse:
    """Upload an original document to MinIO and persist its metadata in PostgreSQL.

    Steps:
    1. Validate file extension against MVP allow-list.
    2. Calculate SHA-256 checksum.
    3. Upload file bytes to MinIO under a deterministic object key.
    4. Write document metadata row via repository.
    5. Return DocumentResponse.

    The caller owns the transaction boundary (commit/rollback).
    """
    extension = _validate_extension(filename)
    checksum = _calculate_checksum(file_bytes)

    document_id = uuid.uuid4()
    bucket = settings.minio_bucket
    object_key = _build_object_key(document_id, extension)

    # Ensure the bucket exists (idempotent).
    found = minio_client.bucket_exists(bucket)
    if not found:
        minio_client.make_bucket(bucket)

    # Upload file to MinIO.
    import io

    file_stream = io.BytesIO(file_bytes)
    file_size = len(file_bytes)
    minio_client.put_object(
        bucket_name=bucket,
        object_name=object_key,
        data=file_stream,
        length=file_size,
        content_type=content_type,
    )

    # Persist metadata in PostgreSQL.
    repo = DocumentsRepository()
    document = await repo.create_document(
        session,
        title=title,
        source_type=source_type,
        access_level=access_level,
        minio_bucket=bucket,
        minio_object_key=object_key,
        checksum=checksum,
        language=language,
        year=year,
        created_by=created_by,
        document_id=document_id,
    )

    return DocumentResponse.model_validate(document)
