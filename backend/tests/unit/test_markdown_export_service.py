import pytest
from app.schemas.answers import AnswerResponse, AnswerSummary, Citation
from app.schemas.search import EvidenceItem, DocumentMetadata
from app.services.exports.markdown_export_service import MarkdownExportService

def test_generate_markdown_full():
    """Test export with all fields populated."""
    service = MarkdownExportService()

    answer_data = AnswerResponse(
        answer=AnswerSummary(summary="This is a synthesized summary.", confidence=0.85),
        evidence=[
            EvidenceItem(
                chunk_id="c1",
                text="Quote one text",
                document_id="d1",
                confidence=0.9,
                metadata=DocumentMetadata(
                    document_id="d1",
                    title="Doc One",
                    source_type="publication"
                )
            )
        ],
        contradictions=["Contradiction A"],
        knowledge_gaps=["Gap B"],
        sources=[Citation(source_id="c1", document_title="Doc One")]
    )

    # Note: EvidenceItem in app/schemas/search probably uses a different metadata object.
    # I will adjust this if the test fails due to Pydantic validation.

    result = service.generate_markdown(answer_data)

    assert "# Grounded Answer" in result
    assert "This is synthesized summary." not in result # typo check
    assert "This is a synthesized summary." in result
    assert "**Confidence Score: 85%**" in result
    assert "## Evidence" in result
    assert "> Quote one text" in result
    assert "*Source: Doc One (ID: c1)*" in result
    assert "## Contradictions" in result
    assert "- Contradiction A" in result
    assert "## Knowledge Gaps" in result
    assert "- Gap B" in result

def test_generate_markdown_minimal():
    """Test export with only required fields."""
    service = MarkdownExportService()

    answer_data = AnswerResponse(
        answer=AnswerSummary(summary="Minimal answer.", confidence=0.5),
        evidence=[],
        contradictions=[],
        knowledge_gaps=[],
        sources=[]
    )

    result = service.generate_markdown(answer_data)

    assert "# Grounded Answer" in result
    assert "Minimal answer." in result
    assert "**Confidence Score: 50%**" in result
    assert "## Evidence" not in result
    assert "## Contradictions" not in result
    assert "## Knowledge Gaps" not in result
