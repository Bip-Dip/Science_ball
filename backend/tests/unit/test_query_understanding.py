import pytest
from unittest import mock
from unittest.mock import AsyncMock
from app.services.query.query_understanding import QueryUnderstandingService, query_understanding_service
from app.schemas.query import QueryIntent
from app.schemas.llm import LLMResponse

@pytest.fixture
def service():
    return QueryUnderstandingService()

@pytest.fixture
def mock_gateway(monkeypatch):
    # Mock the llm_gateway singleton instance from the module
    with mock.patch("app.services.query.query_understanding.llm_gateway") as mocked:
        yield mocked

@pytest.mark.asyncio
async def test_understand_query_success(service, mock_gateway):
    """Test successful LLM extraction and Pydantic validation."""
    # Mock a valid JSON response from the LLM
    valid_json = """
    {
      "intent": "technology_review",
      "query_text": "How does nickel electrowinning work?",
      "materials": ["nickel"],
      "processes": ["electrowinning"],
      "equipment": [],
      "properties": [],
      "geography": [],
      "practice_region": "foreign",
      "year_from": 2015,
      "year_to": null,
      "numeric_conditions": [],
      "source_types": ["publication"],
      "requested_output": {
        "include_graph": true,
        "include_experts": true,
        "include_contradictions": true
      }
    }
    """
    mock_gateway.generate = AsyncMock(return_value=LLMResponse(text=valid_json))

    query = "How does nickel electrowinning work?"
    intent = await service.understand_query(query, lang="en")

    assert isinstance(intent, QueryIntent)
    assert intent.intent == "technology_review"
    assert "nickel" in intent.materials
    assert intent.practice_region == "foreign"
    assert intent.year_from == 2015

@pytest.mark.asyncio
async def test_understand_query_invalid_json(service, mock_gateway):
    """Test that invalid JSON from LLM triggers deterministic fallback."""
    # Mock a response that is not valid JSON (or missing required fields)
    mock_gateway.generate = AsyncMock(return_value=LLMResponse(text="This is just a sentence, not JSON."))

    query = "Some complex query"
    intent = await service.understand_query(query)

    assert isinstance(intent, QueryIntent)
    assert intent.query_text == query
    # In fallback, materials should be empty
    assert len(intent.materials) == 0
    assert intent.intent == "fact_search"

@pytest.mark.asyncio
async def test_understand_query_llm_error(service, mock_gateway):
    """Test that LLM provider error triggers deterministic fallback."""
    from app.services.llm.base import LLMProviderError
    mock_gateway.generate = AsyncMock(side_effect=LLMProviderError("API Timeout"))

    query = "Another query"
    intent = await service.understand_query(query)

    assert isinstance(intent, QueryIntent)
    assert intent.query_text == query
    assert intent.intent == "fact_search"

@pytest.mark.asyncio
async def test_understand_query_markdown_json(service, mock_gateway):
    """Test that JSON wrapped in markdown blocks is correctly extracted."""
    wrapped_json = """
    ```json
    {
      "intent": "fact_search",
      "query_text": "What is the pH of catholyte?",
      "materials": [],
      "processes": [],
      "equipment": [],
      "properties": ["pH"],
      "geography": [],
      "practice_region": null,
      "year_from": null,
      "year_to": null,
      "numeric_conditions": [],
      "source_types": [],
      "requested_output": {
        "include_graph": true,
        "include_experts": true,
        "include_contradictions": true
      }
    }
    ```
    """
    mock_gateway.generate = AsyncMock(return_value=LLMResponse(text=wrapped_json))

    query = "What is the pH of catholyte?"
    intent = await service.understand_query(query, lang="en")

    assert isinstance(intent, QueryIntent)
    assert intent.intent == "fact_search"
    assert "pH" in intent.properties
