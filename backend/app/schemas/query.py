from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class NumericConstraint(BaseModel):
    """Structured numeric filter constraint."""
    property_name: str = Field(..., description="Name of the property (e.g., 'temperature', 'flow_velocity')")
    min_value: Optional[float] = Field(None, description="Minimum value")
    max_value: Optional[float] = Field(None, description="Maximum value")
    unit: str = Field(..., description="Unit of measurement (e.g., 'C', 'm/s')")


class RequestedOutput(BaseModel):
    """Flags indicating what components should be included in the final answer."""
    include_graph: bool = Field(True, description="Include knowledge graph fragment")
    include_experts: bool = Field(True, description="Include related experts")
    include_contradictions: bool = Field(True, description="Include detected contradictions")


class QueryIntent(BaseModel):
    """Structured search intent derived from a natural language query."""
    intent: str = Field(..., description="Type of request (e.g., 'technology_review', 'fact_search', 'comparison')")
    query_text: str = Field(..., description="The original user query")
    materials: List[str] = Field(default_factory=list, description="Extracted material names")
    processes: List[str] = Field(default_factory=list, description="Extracted process names")
    equipment: List[str] = Field(default_factory=list, description="Extracted equipment names")
    properties: List[str] = Field(default_factory=list, description="Relevant technical properties mentioned")
    geography: List[str] = Field(default_factory=list, description="Geographic locations/countries")
    practice_region: Optional[str] = Field(None, description="Filter for 'domestic' (RU) vs 'foreign' (International)")
    year_from: Optional[int] = Field(None, description="Start year filter")
    year_to: Optional[int] = Field(None, description="End year filter")
    numeric_conditions: List[NumericConstraint] = Field(default_factory=list, description="List of specific numeric constraints")
    source_types: List[str] = Field(default_factory=list, description="Preferred source types (e.g., 'patent', 'publication')")
    requested_output: RequestedOutput = Field(default_factory=RequestedOutput)
