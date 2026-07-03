from backend.app.services.llm.base import LLMProvider, LLMProviderError
from backend.app.schemas.llm import LLMRequest, LLMResponse


class MockLLMProvider(LLMProvider):
    async def generate(self, request: LLMRequest) -> LLMResponse:
        # Return a deterministic mock response based on the last user message
        last_message = request.messages[-1].content if request.messages else ""

        if "test error" in last_message.lower():
            raise LLMProviderError("Mock provider simulated error")

        return LLMResponse(
            text=f"[MOCK] Response to: {last_message}",
            usage={"prompt_tokens": 10, "completion_tokens": 20}
        )
