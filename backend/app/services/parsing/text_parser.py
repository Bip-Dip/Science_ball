from __future__ import annotations

from app.services.parsing.base import BaseParser, ParsedContent


class TextParser(BaseParser):
    """Simple parser for plain text files (.txt)."""

    def parse(self, content: bytes) -> ParsedContent:
        try:
            text = content.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            text = content.decode("latin-1")
            encoding = "latin-1"

        return ParsedContent(
            text=text,
            metadata={"encoding": encoding}
        )

# Fix the encoding metadata logic slightly for clarity in final version
