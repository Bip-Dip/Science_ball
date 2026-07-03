import httpx
import logging
from typing import Optional
from backend.app.services.llm.base import LLMProvider, LLMProviderError
from backend.app.schemas.llm import LLMRequest, LLMResponse
from backend.app.settings import settings

logger = logging.getLogger(__name__)

class YandexLLMProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.yandex_api_key
        self.folder_id = settings.yandex_folder_id
        self.model_uri = f"gpt://{self.folder_id}/{settings.yandex_llm_model}/{settings.yandex_llm_model_version}"
        self.endpoint = settings.yandex_llm_endpoint

    async def generate(self, request: LLMRequest) -> LLMResponse:
        # Transform messages to Yandex format
        messages = [
            {"role": msg.role, "text": msg.content}
            for msg in request.messages
        ]

        payload = {
            "modelUri": self.model_uri,
            "completionRequests": [
                {
                    "messages": messages,
                    "temperature": request.temperature if request.temperature is not None else settings.llm_temperature,
                    "maxTokens": request.max_tokens if request.max_tokens is not None else settings.llm_max_tokens,
                }
            ]
        }

        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id,
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()

                # Extract text from the first completion request result
                completion = result["result"]["completionRequests"][0]
                text = completion["text"]

                usage = {
                    "prompt_tokens": completion.get("tokens", {}).get("promptTokens", 0),
                    "completion_tokens": completion.get("tokens", {}).get("completionTokens", 0),
                }

                return LLMResponse(text=text, usage=usage)

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code in (401, 403):
                raise LLMProviderError("Authentication failed with Yandex API") from e
            elif status_code == 429:
                raise LLMProviderError("Yandex API rate limit exceeded") from e
            else:
                raise LLMProviderError(f"Yandex API returned error {status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            raise LLMProviderError("Network error occurred while calling Yandex API") from e
        except (KeyError, IndexError) as e:
            raise LLMProviderError(f"Failed to parse Yandex API response: {str(e)}") from e
        except Exception as e:
            raise LLMProviderError(f"Unexpected error in Yandex provider: {str(e)}") from e
