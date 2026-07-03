from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class LLMMessage(BaseModel):
    role: str = Field(..., description="Role of the message: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Content of the message")


class LLMRequest(BaseModel):
    messages: List[LLMMessage]
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 3000
    json_mode: bool = False


class LLMResponse(BaseModel):
    text: str
    usage: Optional[Dict[str, int]] = None
