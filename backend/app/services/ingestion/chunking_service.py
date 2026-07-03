from typing import List, Dict, Any
from uuid import UUID

from app.repositories.chunks import ChunksRepository
from app.settings import settings


class ChunkingService:
    """Service for deterministic text chunking and persistence."""

    def __init__(self, chunks_repository: ChunksRepository):
        self.chunks_repository = chunks_repository

    def split_text(self, text: str) -> List[str]:
        """
        Splits text into overlapping chunks using a sliding window approach.

        Args:
            text: The raw text to chunk.

        Returns:
            A list of text chunks.
        """
        if not text:
            return []

        size = settings.chunk_size
        overlap = settings.chunk_overlap

        # Ensure overlap is smaller than size to avoid infinite loop or negative step
        effective_overlap = min(overlap, size - 1)
        step = size - effective_overlap

        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end]
            chunks.append(chunk)

            # Break if we reached the end of the text
            if end >= len(text):
                break

            start += step

        return chunks

    async def process_document(
        self,
        session,
        document_id: UUID,
        text: str,
        access_level: str,
        **extra_meta
    ) -> None:
        """
        Chunks a document's text and persists the resulting chunks.
        Implements idempotency by deleting existing chunks first.

        Args:
            session: Database session.
            document_id: ID of the source document.
            text: The full text to chunk.
            access_level: Access level to assign to all chunks.
            **extra_meta: Additional fields like page or section.
        """
        # Idempotency: Remove existing chunks for this document
        await self.chunks_repository.delete_by_document(session, document_id)

        # Deterministically split the text
        text_chunks = self.split_text(text)

        # Prepare chunk data for bulk insertion
        chunks_data = []
        for index, chunk_text in enumerate(text_chunks):
            chunk_payload = {
                "document_id": document_id,
                "chunk_index": index,
                "text": chunk_text,
                "access_level": access_level,
                **extra_meta
            }
            chunks_data.append(chunk_payload)

        # Bulk persist chunks
        if chunks_data:
            await self.chunks_repository.create_many(session, chunks_data)
