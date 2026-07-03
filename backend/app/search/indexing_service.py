from __future__ import annotations

import logging
from typing import Any, Dict, List, Sequence
from elasticsearch.helpers import async_bulk

from app.db.elasticsearch import get_elasticsearch
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.entity import Entity
from app.models.fact import Fact, NumericCondition
from app.search.index_names import ESIndexNames

logger = logging.getLogger(__name__)

class IndexingService:
    """
    Service for transforming PostgreSQL models into Elasticsearch documents
    and performing bulk indexing.
    """

    def __init__(self):
        self.es = get_elasticsearch()

    async def index_document(self, doc: Document) -> None:
        """Index document metadata."""
        body = {
            "document_id": str(doc.id),
            "title": doc.title,
            "source_type": doc.source_type,
            "language": doc.language,
            "year": doc.year,
            # Authors, organizations, geography are not in the current Document model
            # but are defined in mappings. We keep them empty/absent for now to avoid crashes.
            "authors": [],
            "organizations": [],
            "geography": [],
            "practice_region": "foreign", # Default or extracted elsewhere
            "domains": [],
            "access_level": doc.access_level,
        }
        await self.es.index(index=ESIndexNames.DOCS, id=str(doc.id), document=body)

    async def index_chunks(self, chunks: Sequence[Chunk], doc_metadata: Dict[str, Any]) -> None:
        """Index text chunks with inherited document properties."""
        actions = []
        for chunk in chunks:
            # In a real scenario, embeddings would be generated here or passed in.
            # For MVP indexing from DB, we assume they might be missing or handled separately.
            body = {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "text": chunk.text,
                "language": chunk.language,
                "page": chunk.page,
                "section": chunk.section,
                "year": doc_metadata.get("year"),
                "source_type": doc_metadata.get("source_type"),
                "geography": doc_metadata.get("geography", []),
                "practice_region": doc_metadata.get("practice_region", "foreign"),
                "access_level": chunk.access_level,
                "entities": [], # Populated by entity extraction service
                "numeric_conditions": [], # Populated by numeric extractor
                # "embedding": [...] # Added when embedding provider is integrated
            }
            actions.append({
                "_index": ESIndexNames.CHUNKS,
                "_id": str(chunk.id),
                "_source": body
            })

        if actions:
            await async_bulk(self.es, actions)

    async def index_entities(self, entities: Sequence[Entity], doc_metadata: Dict[str, Any]) -> None:
        """Index extracted entities."""
        actions = []
        for entity in entities:
            body = {
                "entity_id": str(entity.id),
                "name": entity.name,
                "canonical_name": entity.canonical_name,
                "type": entity.entity_type,
                "aliases": list(entity.aliases) if entity.aliases else [],
                "access_level": doc_metadata.get("access_level", "internal"),
            }
            actions.append({
                "_index": ESIndexNames.ENTITIES,
                "_id": str(entity.id),
                "_source": body
            })

        if actions:
            await async_bulk(self.es, actions)

    async def index_facts(
        self,
        facts: Sequence[Fact],
        numeric_conditions: Sequence[NumericCondition],
        doc_metadata: Dict[str, Any]
    ) -> None:
        """Index facts and their associated numeric conditions."""
        # Map numeric conditions by fact/source for easy lookup
        # Note: In our model NumericCondition has source_document_id and source_chunk_id.
        # Facts also have these. We link them based on chunk_id.
        cond_map = {}
        for nc in numeric_conditions:
            key = (str(nc.source_document_id), str(nc.source_chunk_id))
            cond_map.setdefault(key, []).append({
                "property": nc.property,
                "min_value": nc.value, # Simplified: using value as min for now
                "max_value": nc.value,
                "unit": nc.unit,
                "raw_text": nc.raw_text
            })

        actions = []
        for fact in facts:
            # Find numeric conditions that apply to this specific source chunk
            key = (str(fact.source_document_id), str(fact.source_chunk_id))
            fact_numeric = cond_map.get(key, [])

            body = {
                "fact_id": str(fact.id),
                "subject": {
                    "id": fact.subject_id,
                    "type": fact.subject_type,
                    "name": "" # Name would need to be fetched from EntitiesRepo
                },
                "predicate": fact.predicate,
                "object": {
                    "id": fact.object_id,
                    "type": fact.object_type,
                    "name": ""
                },
                "numeric": fact_numeric[0] if fact_numeric else None, # ES mapping expects single object or nested
                "source_document_id": str(fact.source_document_id),
                "source_chunk_id": str(fact.source_chunk_id),
                "confidence": float(fact.confidence),
                "verification_status": fact.verification_status,
                "access_level": doc_metadata.get("access_level", "internal"),
            }
            actions.append({
                "_index": ESIndexNames.FACTS,
                "_id": str(fact.id),
                "_source": body
            })

        if actions:
            await async_bulk(self.es, actions)
