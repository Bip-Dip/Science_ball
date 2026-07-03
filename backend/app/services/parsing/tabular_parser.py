from __future__ import annotations

import io
import pandas as pd
from app.services.parsing.base import BaseParser, ParsedContent


class TabularParser(BaseParser):
    """Parser for tabular files (CSV, XLSX) using pandas."""

    def parse(self, content: bytes) -> ParsedContent:
        # Determine file type based on content or we can pass a hint.
        # Since the base interface only takes content, and this parser is
        # specifically used for tabular data, we need to distinguish CSV from XLSX.
        # A simple way is to check the first few bytes (magic numbers).
        if content.startswith(b'PK'):  # Typical start for ZIP/XLSX files
            return self._parse_xlsx(content)
        else:
            return self._parse_csv(content)

    def _parse_csv(self, content: bytes) -> ParsedContent:
        try:
            df = pd.read_csv(io.BytesIO(content))
            text = df.to_string(index=False)
            return ParsedContent(
                text=text,
                metadata={"format": "csv", "rows": len(df), "cols": len(df.columns)}
            )
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}") from e

    def _parse_xlsx(self, content: bytes) -> ParsedContent:
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(io.BytesIO(content))
            sheets_data = []
            all_metadata = {}

            for sheet_name in excel_file.sheet_names:
                df = excel_file.parse(sheet_name)
                sheets_data.append(f"--- Sheet: {sheet_name} ---\n{df.to_string(index=False)}")
                all_metadata[sheet_name] = {"rows": len(df), "cols": len(df.columns)}

            full_text = "\n\n".join(sheets_data)
            return ParsedContent(
                text=full_text,
                metadata={
                    "format": "xlsx",
                    "sheet_count": len(excel_file.sheet_names),
                    "sheets": all_metadata
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to parse XLSX: {str(e)}") from e
