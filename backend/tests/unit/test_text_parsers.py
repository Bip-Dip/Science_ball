from __future__ import annotations

import pytest
import io
import pandas as pd
from docx import Document
import fitz  # PyMuPDF
from app.services.parsing import parsing_service, ParsedContent


def test_text_parser():
    content = b"Hello World\nLine 2"
    result = parsing_service.parse("test.txt", content)
    assert result.text == "Hello World\nLine 2"
    assert result.metadata["encoding"] in ["utf-8", "latin-1"]


def test_markdown_parser():
    content = b"# Header\n**Bold text**"
    result = parsing_service.parse("test.md", content)
    assert result.text == "# Header\n**Bold text**"
    assert result.metadata["format"] == "markdown"


def test_csv_parser():
    # Create a simple CSV in memory
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    content = df.to_csv(index=False).encode("utf-8")

    result = parsing_service.parse("test.csv", content)
    assert "A B" in result.text or "1 3" in result.text
    assert result.metadata["format"] == "csv"
    assert result.metadata["rows"] == 2


def test_xlsx_parser(tmp_path):
    # Create a real XLSX file for the parser to read
    file_path = tmp_path / "test.xlsx"
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    df.to_excel(file_path, index=False)

    with open(file_path, "rb") as f:
        content = f.read()

    result = parsing_service.parse("test.xlsx", content)
    assert "1 3" in result.text or "A B" in result.text
    assert result.metadata["format"] == "xlsx"
    assert result.metadata["sheet_count"] == 1


def test_docx_parser(tmp_path):
    # Create a real DOCX file
    file_path = tmp_path / "test.docx"
    doc = Document()
    doc.add_paragraph("Hello Docx")
    doc.save(file_path)

    with open(file_path, "rb") as f:
        content = f.read()

    result = parsing_service.parse("test.docx", content)
    assert result.text == "Hello Docx"
    assert result.metadata["format"] == "docx"


def test_pdf_parser(tmp_path):
    # Create a real PDF file using PyMuPDF
    file_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello PDF")
    doc.save(file_path)
    doc.close()

    with open(file_path, "rb") as f:
        content = f.read()

    result = parsing_service.parse("test.pdf", content)
    assert "Hello PDF" in result.text
    assert result.metadata["format"] == "pdf"
    assert result.metadata["page_count"] == 1


def test_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file extension"):
        parsing_service.parse("test.exe", b"some binary")


def test_malformed_pdf():
    # Send random bytes to the PDF parser
    with pytest.raises(ValueError, match="Failed to parse PDF"):
        parsing_service.parse("test.pdf", b"not a pdf")


def test_malformed_docx():
    # Send random bytes to the DOCX parser
    with pytest.raises(ValueError, match="Failed to parse DOCX"):
        parsing_service.parse("test.docx", b"not a docx")
