import pytest
from backend.app.services.llm.llm_gateway import LLMGateway
from backend.app.services.llm.mock_provider import MockLLMProvider
from backend.app.services.llm.yandex_provider import YandexLLMProvider
from backend.app.schemas.llm import LLMRequest, LLMMessage
from backend.app.services.llm.base import LLMProviderError
from backend.app.settings import settings

@pytest.fixture
def mock_gateway():
    # Force the gateway to use Mock provider for tests
    import backend.app.services.llm.llm_gateway
    # We can't easily change the singleton, so we create a fresh instance
    # and manually set its provider if needed, or just rely on settings.py
    # Since settings.py defaults to 'mock', it should work by default.
    return LLMGateway()

@pytest.mark.asyncio
async def test_gateway_with_mock_provider():
    gateway = LLMGateway()
    request = LLMRequest(
        messages=[LLMMessage(role="user", content="Hello mock!")]
    )
    response = await gateway.generate(request)
    assert "[MOCK]" in response.text
    assert "Hello mock!" in response.text
    assert response.usage["prompt_tokens"] == 10

@pytest.mark.asyncio
async def test_gateway_error_handling():
    gateway = LLMGateway()
    request = LLMRequest(
        messages=[LLMMessage(role="user", content="test error")]
    )
    with pytest.raises(LLMProviderError):
        await gateway.generate(request)

@pytest.mark.asyncio
async def test_yandex_provider_structure():
    # This test checks if the provider is initialized correctly without making network calls
    provider = YandexLLMProvider()
    assert "gpt://" in provider.model_uri
    assert provider.api_key == settings.yandex_api_key

@pytest.mark.asyncio
async def test_mock_provider_directly():
    provider = MockLLMProvider()
    request = LLMRequest(
        messages=[LLMMessage(role="user", content="Test direct")]
    )
    response = await provider.generate(request)
    assert "Test direct" in response.text
