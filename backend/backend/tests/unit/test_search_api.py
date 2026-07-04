from __future__ import annotations

import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.search.search_service import SearchService
from app.services.query.query_understanding import QueryUnderstandingService
from app.schemas.search import SearchRequest, SearchResponse


@pytest.fixture
def mock_qus():
    """Mock for QueryUnderstandingService."""
    service = MagicMock(spec=QueryUnderstandingService)
    return service


@pytest.fixture
def search_service(mock_qus):
    """Instance of SearchService with mocked dependencies."""
    return SearchService(query_understanding_service=mock_qus)


@pytest.mark.asyncio
async def test_search_api_flow_success(search_service, mock_qus):
    """
    Test the successful flow: NL Query -> Intent -> ES Response -> Evidence.
    We patch 'app.search.search_service.get_elasticsearch' to intercept the call
    inside the service.
    """
    # 1. Mock QueryUnderstandingService to return a valid intent
    from app.schemas.query import QueryIntent, RequestedOutput
    mock_qus.understand_query.return_value = QueryIntent(
        intent="technology_review",
        query_text="nickel electrowinning",
        requested_output=RequestedOutput()
    )

    # 2. Mock the Elasticsearch client
    with unittest.mock.patch("app.search.search_service.get_elasticsearch") as mock_get_es:
        mock_es = AsyncMock()
        mock_get_es.return_value = mock_es

        # Mock search for chunks (first call) and doc enrichment (second call)
        mock_es.search.side_effect = [
            { # First call: chunks
                "hits": {
                    "total": {"value": 1},
                    "hits": [{
                        "_score": 1.5,
                        "_source": {
                            "chunk_id": "c1",
                            "document_id": "d1",
                            "text": "Nickel electrowinning is...",
                            "page": 1,
                            "section": "Intro"
                        }
                    }]
                }
            },
            { # Second call: doc metadata enrichment
                "hits": {
                    "total": {"value": 1},
                    "hits": [{
                        "_source": {
                            "title": "Nickel Review",
                            "source_type": "publication",
                            "year": 2020,
                            "language": "en",
                            "geography": ["Canada"],
                            "practice_region": "foreign"
                        }
                    }]
                }
            }
        ]

        request = SearchRequest(query="nickel electrowinning")
        response = await search_service.search(request, allowed_access_levels=["public"])

        assert isinstance(response, SearchResponse)
        assert response.total_hits == 1
        assert len(response.results) == 1
        assert response.results[0].text == "Nickel electrowinning is..."
        assert response.results[0].metadata.title == "Nickel Review"
        assert response.results[0].document_id == "d1"


@pytest.mark.asyncio
async def test_search_api_no_results(search_service, mock_qus):
    """Test behavior when no chunks are found."""
    from app.schemas.query import QueryIntent, RequestedOutput
    mock_qus.understand_query.return_value = QueryIntent(
        intent="fact_search",
        query_text="nonexistent process",
        requested_output=RequestedOutput()
    )

    with unittest.mock.patch("app.search.search_service.get_elasticsearch") as mock_get_es:
        mock_es = AsyncMock()
        mock_get_es.return_value = mock_es
        mock_es.search.return_value = {
            "hits": {"total": {"value": 0}, "hits": []}
        }

        request = SearchRequest(query="nonexistent process")
        response = await search_service.search(request, allowed_access_levels=["public"])

        assert response.total_hits == 0
        assert len(response.results) == 0
