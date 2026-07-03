from __future__ import annotations

import io
from docx import Document
from app.services.parsing.base import BaseParser, ParsedContent


class DocxParser(BaseParser):
    """Parser for DOCX files using python-docx."""

    def parse(self, content: bytes) -> ParsedContent:
        try:
            # Create a file-like object from bytes
            file_stream = io.BytesIO(content)
            doc = Document(file_stream)

            # Extract text from paragraphs
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)

            return ParsedContent(
                text=full_text,
                metadata={
                    "format": "docx",
                    "paragraph_count": len(paragraphs)
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}") from e
