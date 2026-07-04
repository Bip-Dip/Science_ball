from __future__ import annotations

import time
from typing import List, Dict, Any, Optional
from fastapi import Depends
from app.db.elasticsearch import get_elasticsearch
from app.search.index_names import ESIndexNames
from app.search.query_builder import SearchQueryBuilder
from app.services.query.query_understanding import QueryUnderstandingService
from app.schemas.search import SearchRequest, SearchResponse, EvidenceItem, DocumentMetadata
from app.schemas.query import QueryIntent


class SearchService:
    """
    Orchestrates the search workflow: NL query -> Intent -> ES DSL -> Results -> Enrichment.
    """

    def __init__(self, query_understanding_service: QueryUnderstandingService):
        self.qus = query_understanding_service
        self.query_builder = SearchQueryBuilder()

    async def search(
        self,
        request: SearchRequest,
        allowed_access_levels: List[str]
    ) -> SearchResponse:
        start_time = time.perf_counter()

        # 1. Understand the query (NL -> QueryIntent)
        intent: QueryIntent = await self.qus.understand_query(request.query)

        # If user provided explicit filters in request, they could override intent here.
        # For MVP, we use the derived intent.

        # 2. Build the ES DSL query
        es_query = self.query_builder.build_chunks_query(intent, allowed_access_levels)

        # 3. Execute search against rd_chunks_v1 index
        es = get_elasticsearch()
        response = await es.search(
            index=ESIndexNames.CHUNKS,
            query=es_query,
            size=20  # Top 20 results for basic search
        )

        hits = response["hits"]["hits"]
        total_hits = response["hits"]["total"]["value"]

        # 4. Enrichment: Fetch document metadata for each chunk
        evidence: List[EvidenceItem] = []
        for hit in hits:
            source = hit["_source"]
            doc_id = source["document_id"]

            # We fetch the doc metadata from rd_docs_v1 index.
            # In a high-load system, we'd use a cache or a join-like operation.
            doc_resp = await es.search(
                index=ESIndexNames.DOCS,
                query={"term": {"document_id": doc_id}},
                size=1
            )

            doc_data = {}
            if doc_resp["hits"]["hits"]:
                doc_data = doc_resp["hits"]["hits"][0]["_source"]

            evidence.append(EvidenceItem(
                chunk_id=source["chunk_id"],
                document_id=doc_id,
                text=source["text"],
                confidence=hit["_score"], # Using ES score as proxy for confidence in basic search
                page=source.get("page"),
                section=source.get("section"),
                metadata=DocumentMetadata(
                    document_id=doc_id,
                    title=doc_data.get("title", "Unknown Title"),
                    source_type=doc_data.get("source_type", "unknown"),
                    year=doc_data.get("year"),
                    language=doc_data.get("language"),
                    geography=doc_data.get("geography", []),
                    practice_region=doc_data.get("practice_region")
                )
            ))

        execution_time = (time.perf_counter() - start_time) * 1000

        return SearchResponse(
            query=request.query,
            results=evidence,
            total_hits=total_hits,
            execution_time_ms=execution_time
        )
