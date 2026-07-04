from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class GraphNode(BaseModel):
    id: str
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphNeighborhood(BaseModel):
    center_node_id: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class NeighborhoodRequest(BaseModel):
    node_id: str
    label: str
    depth: Optional[int] = 1
