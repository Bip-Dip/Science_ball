import logging
import json
from typing import Optional
from pathlib import Path

from app.schemas.query import QueryIntent, RequestedOutput
from app.services.llm.llm_gateway import llm_gateway
from app.services.llm.base import LLMProviderError
from app.schemas.llm import LLMRequest

logger = logging.getLogger(__name__)

class QueryUnderstandingService:
    """
    Service to transform natural language queries into structured search intent.
    Uses LLMGateway for extraction and provides deterministic fallback.
    """
    def __init__(self):
        # Prompts are stored in the filesystem as per SDD structure
        # Use absolute path relative to project root or resolve based on current file
        base_dir = Path(__file__).resolve().parent.parent.parent # services/query -> services -> app
        self.prompts_path = base_dir / "prompts"

    def _load_prompt(self, lang: str) -> str:
        """Load prompt from markdown file based on language."""
        file_name = f"query_understanding.{lang}.md"
        file_path = self.prompts_path / file_name
        try:
            return file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"Prompt file {file_name} not found. Falling back to English.")
            # Fallback to English if the specific language prompt is missing
            en_path = self.prompts_path / "query_understanding.en.md"
            return en_path.read_text(encoding="utf-8")

    async def understand_query(self, query: str, lang: str = "ru") -> QueryIntent:
        """
        Analyzes the user query and returns a validated QueryIntent object.

        Args:
            query: The raw user input string.
            lang: Language of the query ('ru' or 'en').

        Returns:
            A validated QueryIntent Pydantic model.
        """
        prompt_template = self._load_prompt(lang)

        # We inject the actual query into the prompt (simplified for MVP,
        # in a real system we'd use a more robust template engine).
        full_prompt = f"{prompt_template}\n\nUser Query: {query}"

        messages = [
            {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
            {"role": "user", "content": full_prompt}
        ]

        try:
            # Call LLM via gateway. We request json_mode if the provider supports it.
            response = await llm_gateway.generate(
                LLMRequest(
                    messages=messages,
                    json_mode=True
                )
            )

            # Extract text from response (the Gateway handles provider-specific wrappers)
            content = response.text.strip()

            # Clean potential markdown markers if LLM ignores 'no markdown' instruction
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0]
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0]

            # Validate against Pydantic schema
            return QueryIntent.model_validate_json(content)

        except (LLMProviderError, ValueError, Exception) as e:
            logger.error(f"Query understanding failed for query '{query}': {str(e)}")
            return self._deterministic_fallback(query)

    def _deterministic_fallback(self, query: str) -> QueryIntent:
        """
        Creates a basic search intent when LLM extraction fails.
        This ensures the system remains operational and can still perform
        basic full-text search.
        """
        logger.info(f"Applying deterministic fallback for query: {query}")
        return QueryIntent(
            intent="fact_search", # Default to a general fact search
            query_text=query,
            materials=[],
            processes=[],
            equipment=[],
            properties=[],
            geography=[],
            practice_region=None,
            year_from=None,
            year_to=None,
            numeric_conditions=[],
            source_types=[],
            requested_output=RequestedOutput()
        )

# Singleton instance for the application
query_understanding_service = QueryUnderstandingService()
