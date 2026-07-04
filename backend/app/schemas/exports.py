from pydantic import BaseModel
from app.schemas.answers import AnswerResponse

class MarkdownExportRequest(BaseModel):
    """Request to export a synthesized answer as a Markdown file."""
    answer_data: AnswerResponse
