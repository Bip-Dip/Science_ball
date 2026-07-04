from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.search import SearchRequest, SearchResponse
from app.search.search_service import SearchService
from app.services.query.query_understanding import QueryUnderstandingService
from app.dependencies import get_current_user # Assuming this exists or will be needed for access_level

router = APIRouter(prefix="/search", tags=["Search"])

# Dependency to provide the search service
def get_search_service(
    query_understanding_service: QueryUnderstandingService = Depends()
) -> SearchService:
    return SearchService(query_understanding_service)

@router.post("", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def search(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
    # In a real scenario, we get the user from JWT token via dependency
    # For MVP/Development, we might use a dummy access list or current_user.access_levels
    current_user_access_levels: list[str] = ["public", "internal"]
):
    """
    Basic search endpoint. Performs natural language query understanding,
    executes Elasticsearch search with mandatory access filtering,
    and returns ranked evidence items.
    """
    try:
        return await search_service.search(
            request=request,
            allowed_access_levels=current_user_access_levels
        )
    except Exception as e:
        # Log the exception here in a real app
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
