from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.auth_service import AuthService, get_current_user_dep
from ..services.section_service import SectionService

router = APIRouter(prefix="/projects/{project_id}/sections", tags=["sections"])

@router.post(
    "/",
    response_model=schemas.SectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new section"
)
async def create_section(
    project_id: UUID,
    section_data: schemas.SectionBase,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new section in a project.
    
    - **title**: Section title
    - **content**: Section content
    - **idx**: Position in the document
    """
    section_service = SectionService(db)
    try:
        return await section_service.create_section(
            project_id=project_id,
            user_id=current_user.id,
            section_data=section_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the section"
        ) from e

@router.get(
    "/",
    response_model=schemas.SectionListResponse,
    summary="List all sections in a project"
)
async def list_sections(
    project_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: str = Query(None, description="Search by section title or content"),
    initial_only: bool = Query(False, description="Only return initially generated sections"),
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    List sections in a project with optional filtering and pagination.
    """
    section_service = SectionService(db)
    try:
        sections, total = await section_service.list_sections(
            project_id=project_id,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            search=search,
            initial_only=initial_only
        )
        return {
            "items": sections,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching sections"
        ) from e

@router.get(
    "/{section_id}",
    response_model=schemas.SectionResponse,
    summary="Get section details"
)
async def get_section(
    project_id: UUID,
    section_id: UUID,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get details of a specific section.
    """
    section_service = SectionService(db)
    try:
        section = await section_service.get_section(
            section_id=section_id,
            project_id=project_id,
            user_id=current_user.id
        )
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        return section
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the section"
        ) from e

@router.put(
    "/{section_id}",
    response_model=schemas.SectionResponse,
    summary="Update a section"
)
async def update_section(
    project_id: UUID,
    section_id: UUID,
    section_data: schemas.SectionUpdate,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a section's details.
    """
    section_service = SectionService(db)
    try:
        section = await section_service.update_section(
            section_id=section_id,
            project_id=project_id,
            user_id=current_user.id,
            update_data=section_data
        )
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        return section
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the section"
        ) from e

@router.delete(
    "/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a section"
)
async def delete_section(
    project_id: UUID,
    section_id: UUID,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a section.
    """
    section_service = SectionService(db)
    try:
        success = await section_service.delete_section(
            section_id=section_id,
            project_id=project_id,
            user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        return None
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the section"
        ) from e
