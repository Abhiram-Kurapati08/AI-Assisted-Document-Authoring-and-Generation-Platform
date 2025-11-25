from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.auth_service import AuthService, get_current_user_dep
from ..services.export_service import ExportService

router = APIRouter(prefix="/projects/{project_id}/export", tags=["export"])

@router.get(
    "/",
    response_class=StreamingResponse,
    summary="Export project to a document"
)
async def export_project(
    project_id: UUID,
    format: str = Query("docx", description="Export format (docx, pptx, txt)"),
    include_comments: bool = Query(False, description="Include comments in the export"),
    include_revision_history: bool = Query(False, description="Include revision history (DOCX only)"),
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Export a project to the specified format.
    
    Supported formats:
    - docx: Microsoft Word Document
    - pptx: Microsoft PowerPoint Presentation
    - txt: Plain Text
    
    Returns:
        The exported file as a downloadable attachment
    """
    export_service = ExportService(db)
    try:
        content, content_type, filename = await export_service.export_document(
            project_id=project_id,
            user_id=current_user.id,
            export_format=format,
            include_comments=include_comments,
            include_revision_history=include_revision_history and format == "docx"
        )
        
        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(content))
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting project: {str(e)}"
        ) from e

@router.post(
    "/custom",
    response_class=StreamingResponse,
    summary="Export project with custom settings"
)
async def export_project_custom(
    project_id: UUID,
    export_data: schemas.ExportRequest,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Export a project with custom settings.
    
    - **format**: The export format (docx, pptx, txt, pdf)
    - **include_comments**: Whether to include comments
    - **include_revision_history**: Whether to include revision history (DOCX only)
    - **document_style**: Custom document styling (for DOCX)
    - **presentation_style**: Custom presentation styling (for PPTX)
    - **custom_styles**: Additional custom styles
    """
    export_service = ExportService(db)
    try:
        content, content_type, filename = await export_service.export_document(
            project_id=project_id,
            user_id=current_user.id,
            export_format=export_data.format,
            include_comments=export_data.include_comments,
            include_revision_history=export_data.include_revision_history and export_data.format == "docx"
        )
        
        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(content))
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting project: {str(e)}"
        ) from e
