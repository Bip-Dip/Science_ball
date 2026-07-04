from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.graph import NeighborhoodRequest, GraphNeighborhood
from app.services.graph.graph_query_service import GraphQueryService
from app.dependencies import get_current_user # Assuming this is where user context comes from

router = APIRouter(prefix="/graph", tags=["Graph"])

def get_graph_service() -> GraphQueryService:
    return GraphQueryService()

@router.post("/neighborhood", response_model=GraphNeighborhood, status_code=status.HTTP_200_OK)
async def get_neighborhood(
    request: NeighborhoodRequest,
    graph_service: GraphQueryService = Depends(get_graph_service),
    # For MVP we use a dummy access list.
    # In production this would be derived from the current_user dependency.
    current_user_access_levels: list[str] = ["public", "internal"]
):
    """
    Returns a small neighborhood of nodes and edges around a given node,
    filtered by the user's access levels.
    """
    try:
        return await graph_service.get_neighborhood(
            node_id=request.node_id,
            label=request.label,
            depth=request.depth,
            allowed_access_levels=current_user_access_levels
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph query failed: {str(e)}"
        )
