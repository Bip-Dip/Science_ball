from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Basic metadata of the document associated with a chunk."""
    document_id: str
    title: str
    source_type: str
    year: Optional[int] = None
    language: Optional[str] = None
    geography: List[str] = Field(default_factory=list)
    practice_region: Optional[str] = None


class EvidenceItem(BaseModel):
    """A single search result representing a piece of evidence."""
    chunk_id: str
    document_id: str
    text: str
    confidence: float
    page: Optional[int] = None
    section: Optional[str] = None
    metadata: DocumentMetadata


class SearchResponse(BaseModel):
    """The full response from the basic search API."""
    query: str
    results: List[EvidenceItem]
    total_hits: int
    execution_time_ms: float


class SearchRequest(BaseModel):
    """Incoming request for a basic search."""
    query: str = Field(..., min_length=1, description="The natural language query")
    # Optional explicit filters that might override or augment the NL intent
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional manual filters (e.g., {'year_from': 2020, 'practice_region': 'foreign'})"
    )
