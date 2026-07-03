from __future__ import annotations

from typing import Dict, Type
from app.services.parsing.base import BaseParser, ParsedContent
from app.services.parsing.text_parser import TextParser
from app.services.parsing.markdown_parser import MarkdownParser
from app.services.parsing.pdf_parser import PDFParser
from app.services.parsing.docx_parser import DocxParser
from app.services.parsing.tabular_parser import TabularParser


class ParsingService:
    """Dispatcher service that selects the appropriate parser based on file extension."""

    def __init__(self):
        # Mapping extensions to parser classes
        self._parsers: Dict[str, BaseParser] = {
            ".txt": TextParser(),
            ".md": MarkdownParser(),
            ".pdf": PDFParser(),
            ".docx": DocxParser(),
            ".csv": TabularParser(),
            ".xlsx": TabularParser(),
        }

    def parse(self, filename: str, content: bytes) -> ParsedContent:
        """
        Parse a file based on its extension.

        Args:
            filename: The name of the file (used to extract extension).
            content: Raw bytes of the file.

        Returns:
            ParsedContent containing extracted text and metadata.

        Raises:
            ValueError: If no parser is available for the given extension.
        """
        import os
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        parser = self._parsers.get(ext)
        if not parser:
            raise ValueError(f"Unsupported file extension '{ext}'. Supported: {list(self._parsers.keys())}")

        return parser.parse(content)

# Singleton instance for easy access
parsing_service = ParsingService()
