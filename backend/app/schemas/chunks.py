from pydantic import ConfigDict, BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    text: str
    language: Optional[str]
    page: Optional[int]
    section: Optional[str]
    access_level: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
