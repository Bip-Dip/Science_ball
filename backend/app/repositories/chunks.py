from typing import Sequence, List
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk


class ChunksRepository:
    """Repository for handling persistence of text chunks."""

    async def create(self, session: AsyncSession, chunk_data: dict) -> Chunk:
        """Persist a single chunk."""
        chunk = Chunk(**chunk_data)
        session.add(chunk)
        await session.flush()
        return chunk

    async def create_many(self, session: AsyncSession, chunks_data: List[dict]) -> None:
        """Bulk insert chunks for efficiency."""
        chunks = [Chunk(**data) for data in chunks_data]
        session.add_all(chunks)
        await session.flush()

    async def get_by_document(self, session: AsyncSession, document_id: UUID) -> Sequence[Chunk]:
        """Retrieve all chunks for a specific document ordered by index."""
        query = (
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def delete_by_document(self, session: AsyncSession, document_id: UUID) -> None:
        """Remove all chunks associated with a document."""
        stmt = delete(Chunk).where(Chunk.document_id == document_id)
        await session.execute(stmt)
