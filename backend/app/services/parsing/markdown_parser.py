from __future__ import annotations

from app.services.parsing.base import BaseParser, ParsedContent


class MarkdownParser(BaseParser):
    """Simple parser for Markdown files (.md)."""

    def parse(self, content: bytes) -> ParsedContent:
        # For MVP, Markdown is treated as text but we mark it in metadata
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

        return ParsedContent(
            text=text,
            metadata={"format": "markdown"}
        )
