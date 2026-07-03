from __future__ import annotations

import logging
import uuid
from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chunks import ChunksRepository
from app.repositories.documents import DocumentsRepository
from app.repositories.entities import EntitiesRepository
from app.repositories.facts import FactsRepository
from app.graph.graph_writer import GraphWriter

logger = logging.getLogger(__name__)

class GraphStep:
    """
    Orchestrates the population of the Neo4j knowledge graph for a single document.
    Ensures that documents, chunks, entities and facts are written as nodes/edges.
    """

    def __init__(
        self,
        graph_writer: GraphWriter,
        docs_repo: DocumentsRepository,
        chunks_repo: ChunksRepository,
        entities_repo: EntitiesRepository,
        facts_repo: FactsRepository,
    ):
        self.graph_writer = graph_writer
        self.docs_repo = docs_repo
        self.chunks_repo = chunks_repo
        self.entities_repo = entities_repo
        self.facts_repo = facts_repo

    async def execute(self, session: AsyncSession, document_id: uuid.UUID) -> bool:
        """
        Execute the graph population flow for a document.
        Returns True if successful, False otherwise.
        """
        try:
            # 1. Document Node
            doc = await self.docs_repo.get_by_id(session, document_id)
            if not doc:
                logger.error(f"Document {document_id} not found for graph writing")
                return False

            await self.graph_writer.write_node(
                label="Document",
                node_id=str(doc.id),
                properties={
                    "title": doc.title,
                    "source_type": doc.source_type,
                    "year": doc.year,
                    "access_level": doc.access_level,
                }
            )

            # 2. Chunk Nodes & Document -> Chunk links
            chunks = await self.chunks_repo.get_by_document(session, document_id)
            if chunks:
                chunk_nodes = []
                for c in chunks:
                    chunk_nodes.append({
                        "label": "Chunk",
                        "id": str(c.id),
                        "props": {
                            "index": c.chunk_index,
                            "page": c.page,
                            "access_level": c.access_level,
                        }
                    })
                await self.graph_writer.write_nodes_batch(chunk_nodes)

                # Links: (:Document)-[:HAS_CHUNK]->(:Chunk)
                links = [
                    {
                        "from": {"id": str(doc.id), "label": "Document"},
                        "to": {"id": str(c.id), "label": "Chunk"},
                        "type": "HAS_CHUNK",
                        "props": {}
                    }
                    for c in chunks
                ]
                await self.graph_writer.write_relationships_batch(links)

            # 3. Entity Nodes & Chunk -> Entity links
            entities = await self.entities_repo.get_by_document(session, document_id)
            if entities:
                entity_nodes = []
                for e in entities:
                    entity_nodes.append({
                        "label": e.entity_type, # Material, Process, etc.
                        "id": e.canonical_name or e.name,
                        "props": {
                            "name": e.name,
                            "canonical_name": e.canonical_name,
                            "confidence": e.confidence,
                            "extraction_method": e.extraction_method,
                        }
                    })
                await self.graph_writer.write_nodes_batch(entity_nodes)

                # Links: (:Chunk)-[:MENTIONS]->(:Entity)
                mentions = []
                for e in entities:
                    if e.chunk_id:
                        mentions.append({
                            "from": {"id": str(e.chunk_id), "label": "Chunk"},
                            "to": {"id": e.canonical_name or e.name, "label": e.entity_type},
                            "type": "MENTIONS",
                            "props": {}
                        })
                await self.graph_writer.write_relationships_batch(mentions)

            # 4. Fact Relationships (Entity -> Entity)
            facts = await self.facts_repo.get_by_document(session, document_id)
            if facts:
                fact_rels = []
                for f in facts:
                    fact_rels.append({
                        "from": {"id": f.subject_id, "label": f.subject_type},
                        "to": {"id": f.object_id, "label": f.object_type},
                        "type": f.predicate,
                        "props": {
                            "fact_id": str(f.id),
                            "confidence": f.confidence,
                            "source_document_id": str(f.source_document_id),
                            "verification_status": f.verification_status,
                            "updated_at": f.updated_at.isoformat() if f.updated_at else None,
                        }
                    })
                await self.graph_writer.write_relationships_batch(fact_rels)

            logger.info(f"Successfully wrote graph for document {document_id}")
            return True

        except Exception as e:
            logger.exception(f"Graph writing failed for document {document_id}: {str(e)}")
            return False
