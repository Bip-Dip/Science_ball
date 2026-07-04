from fastapi import APIRouter, Depends, Response
from app.schemas.exports import MarkdownExportRequest
from app.services.exports.markdown_export_service import MarkdownExportService

router = APIRouter()

def get_markdown_export_service() -> MarkdownExportService:
    return MarkdownExportService()

@router.post("/markdown", response_class=Response)
async def export_to_markdown(
    request: MarkdownExportRequest,
    service: MarkdownExportService = Depends(get_markdown_export_service)
):
    """
    Exports a synthesized answer into a downloadable Markdown file.
    """
    try:
        markdown_content = service.generate_markdown(request.answer_data)

        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": 'attachment; filename="knowledge_map_export.md"'
            }
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
