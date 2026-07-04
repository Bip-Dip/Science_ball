import logging
from app.schemas.answers import AnswerResponse

logger = logging.getLogger(__name__)

class MarkdownExportService:
    """
    Service for transforming synthesized answers into formatted Markdown reports.
    """

    def generate_markdown(self, answer_data: AnswerResponse) -> str:
        """
        Transforms an AnswerResponse object into a professional Markdown report.
        """
        lines = []

        # 1. Title and Summary
        lines.append("# Grounded Answer")
        lines.append("")
        lines.append(answer_data.answer.summary)
        lines.append("")

        # 2. Confidence Score
        confidence_pct = int(answer_data.answer.confidence * 100)
        lines.append(f"**Confidence Score: {confidence_pct}%**")
        lines.append("")

        # 3. Evidence Section
        if answer_data.evidence:
            lines.append("## Evidence")
            for item in answer_data.evidence:
                # Find corresponding citation for the source title
                citation = next(
                    (c for c in answer_data.sources if c.source_id == item.chunk_id),
                    None
                )
                source_title = citation.document_title if citation else "Unknown Source"

                # Use blockquote for the actual quote from the document
                lines.append(f"> {item.text}")
                lines.append(f"  *Source: {source_title} (ID: {item.chunk_id})*")
                lines.append("")

        # 4. Contradictions Section
        if answer_data.contradictions:
            lines.append("## Contradictions")
            for contradiction in answer_data.contradictions:
                lines.append(f"- {contradiction}")
            lines.append("")

        # 5. Knowledge Gaps Section
        if answer_data.knowledge_gaps:
            lines.append("## Knowledge Gaps")
            for gap in answer_data.knowledge_gaps:
                lines.append(f"- {gap}")
            lines.append("")

        return "\n".join(lines).strip()
