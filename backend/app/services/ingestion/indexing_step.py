from __future__ import annotations

import logging
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chunks import ChunksRepository
from app.repositories.documents import DocumentsRepository
from app.repositories.entities import EntitiesRepository
from app.repositories.facts import FactsRepository
from app.search.indexing_service import IndexingService

logger = logging.getLogger(__name__)

class IndexingStep:
    """
    Orchestrates the indexing process for a single document.
    Fetches all related records from PostgreSQL and pushes them to Elasticsearch.
    """

    def __init__(
        self,
        indexing_service: IndexingService,
        docs_repo: DocumentsRepository,
        chunks_repo: ChunksRepository,
        entities_repo: EntitiesRepository,
        facts_repo: FactsRepository,
    ):
        self.indexing_service = indexing_service
        self.docs_repo = docs_repo
        self.chunks_repo = chunks_repo
        self.entities_repo = entities_repo
        self.facts_repo = facts_repo

    async def execute(self, session: AsyncSession, document_id: uuid.UUID) -> bool:
        """
        Perform the indexing flow for a document.
        Returns True if successful, False otherwise.
        """
        try:
            # 1. Fetch Document Metadata
            doc = await self.docs_repo.get_by_id(session, document_id)
            if not doc:
                logger.error(f"Document {document_id} not found for indexing")
                return False

            doc_metadata = {
                "title": doc.title,
                "source_type": doc.source_type,
                "language": doc.language,
                "year": doc.year,
                "access_level": doc.access_level,
                # Add other fields if available in Document model
            }

            # 2. Index Document
            await self.indexing_service.index_document(doc)

            # 3. Fetch and Index Chunks
            chunks = await self.chunks_repo.get_by_document(session, document_id)
            if chunks:
                await self.indexing_service.index_chunks(chunks, doc_metadata)

            # 4. Fetch and Index Entities
            entities = await self.entities_repo.get_by_document(session, document_id)
            if entities:
                await self.indexing_service.index_entities(entities, doc_metadata)

            # 5. Fetch and Index Facts (and their Numeric Conditions)
            facts = await self.facts_repo.get_by_document(session, document_id)
            if facts:
                # We need numeric conditions associated with this document
                # Since the repository might not have a direct 'get_by_document' for NCs,
                # we assume they are fetched via facts or a separate repo call.
                # For now, let's check if FactsRepository can provide them or use a raw query.
                # Based on models, NumericCondition has source_document_id.
                from app.repositories.facts import FactsRepository # for type hint
                numeric_conditions = await self.facts_repo.get_numeric_conditions_by_document(session, document_id)
                await self.indexing_service.index_facts(facts, numeric_conditions, doc_metadata)

            logger.info(f"Successfully indexed document {document_id} and its artifacts to ES")
            return True

        except Exception as e:
            logger.exception(f"Indexing failed for document {document_id}: {str(e)}")
            return False
