import logging
from typing import Optional
from app.settings import settings
from app.services.llm.base import LLMProvider, LLMProviderError
from app.services.llm.mock_provider import MockLLMProvider
from app.services.llm.yandex_provider import YandexLLMProvider
from app.schemas.llm import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)

class LLMGateway:
    def __init__(self):
        # Initialize the provider based on settings
        provider_type = settings.llm_provider.lower()
        if provider_type == "yandex":
            self._provider = YandexLLMProvider()
        elif provider_type == "mock":
            self._provider = MockLLMProvider()
        else:
            # Default to mock for safety in dev/test
            logger.warning(f"Unknown LLM provider '{provider_type}'. Falling back to MockLLMProvider.")
            self._provider = MockLLMProvider()

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Facade method to generate text from the active LLM provider.
        Implements timeout and retry logic at the gateway boundary if needed.
        """
        # For MVP, we rely on the individual providers for low-level timeouts (via httpx)
        # but we can wrap this in a retry loop here if required by SDD.
        max_retries = settings.llm_max_retries
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return await self._provider.generate(request)
            except LLMProviderError as e:
                last_exception = e
                # Only retry on certain types of errors (e.g., rate limits or network issues)
                # If it's an auth error, no point in retrying.
                if "Authentication failed" in str(e):
                    break

                if attempt < max_retries:
                    logger.info(f"LLMGateway retry {attempt + 1}/{max_retries} after error: {str(e)}")
                else:
                    logger.error(f"LLMGateway failed after {max_retries + 1} attempts: {str(e)}")

        raise last_exception or LLMProviderError("An unexpected error occurred in LLMGateway")

# Singleton instance for the application
llm_gateway = LLMGateway()
