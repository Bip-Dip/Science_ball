from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedContent:
    """Standard output of any text parser."""
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    # metadata can contain:
    # - 'pages': list of page texts or markers
    # - 'sections': structure info
    # - 'sheets': for tabular data
    # - 'page_count': total pages


class BaseParser(ABC):
    """Abstract base class for all document parsers."""

    @abstractmethod
    def parse(self, content: bytes) -> ParsedContent:
        """
        Parse the binary content of a file and return extracted text.

        Args:
            content: Raw bytes of the file to be parsed.

        Returns:
            ParsedContent object containing text and metadata.

        Raises:
            ValueError: If the content is malformed or cannot be parsed.
        """
        pass
