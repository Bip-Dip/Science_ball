from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from backend.app.schemas.llm import LLMRequest, LLMResponse


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        request: LLMRequest
    ) -> LLMResponse:
        """
        Generate a text response based on the provided messages.
        """
        pass
