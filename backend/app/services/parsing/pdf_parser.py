from __future__ import annotations

import fitz  # PyMuPDF
from app.services.parsing.base import BaseParser, ParsedContent


class PDFParser(BaseParser):
    """Parser for PDF files using PyMuPDF."""

    def parse(self, content: bytes) -> ParsedContent:
        try:
            # Open PDF from memory stream
            doc = fitz.open(stream=content, filetype="pdf")

            pages_text = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pages_text.append(page.get_text())

            full_text = "\n\n".join(
                [f"[Page {i+1}]\n{text}" for i, text in enumerate(pages_text)]
            )

            return ParsedContent(
                text=full_text,
                metadata={
                    "page_count": len(doc),
                    "pages": pages_text,
                    "format": "pdf"
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}") from e
