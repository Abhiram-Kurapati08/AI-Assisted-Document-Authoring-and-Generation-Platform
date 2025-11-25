from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.auth_service import AuthService, get_current_user_dep
from ..services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post(
    "/",
    response_model=schemas.ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project"
)
async def create_project(
    project_data: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new project.
    
    - **title**: Project title
    - **doc_type**: Document type (docx or pptx)
    - **topic_prompt**: Optional prompt describing the project topic
    """
    project_service = ProjectService(db)
    try:
        return await project_service.create_project(project_data, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/",
    response_model=schemas.ProjectListResponse,
    summary="List all projects for the current user"
)
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: str = Query(None, description="Search by project title"),
    doc_type: str = Query(None, description="Filter by document type"),
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    List all projects for the current user with optional filtering and pagination.
    """
    project_service = ProjectService(db)
    try:
        projects, total = await project_service.list_projects(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            search=search,
            doc_type=doc_type
        )
        return {
            "items": projects,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching projects"
        ) from e

@router.get(
    "/{project_id}",
    response_model=schemas.ProjectResponse,
    summary="Get project details"
)
async def get_project(
    project_id: UUID,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get details of a specific project by ID.
    """
    project_service = ProjectService(db)
    try:
        project = await project_service.get_project(project_id, current_user.id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the project"
        ) from e

@router.put(
    "/{project_id}",
    response_model=schemas.ProjectResponse,
    summary="Update a project"
)
async def update_project(
    project_id: UUID,
    project_data: schemas.ProjectUpdate,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a project's details.
    """
    project_service = ProjectService(db)
    try:
        project = await project_service.update_project(
            project_id=project_id,
            user_id=current_user.id,
            update_data=project_data
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the project"
        ) from e

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project"
)
async def delete_project(
    project_id: UUID,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a project and all its associated sections and content.
    """
    project_service = ProjectService(db)
    try:
        success = await project_service.delete_project(project_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return None
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the project"
        ) from e

@router.post(
    "/{project_id}/generate",
    response_model=List[schemas.SectionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate initial content for a project"
)
async def generate_project_content(
    project_id: UUID,
    generate_data: schemas.ProjectGenerateRequest,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Generate initial content sections for a project using AI.
    
    - **num_sections**: Number of sections to generate (1-20)
    - **include_outline**: Whether to include an outline
    - **outline_format**: Optional format for the outline
    """
    project_service = ProjectService(db)
    try:
        return await project_service.generate_initial_content(
            project_id=project_id,
            user_id=current_user.id,
            num_sections=generate_data.num_sections,
            include_outline=generate_data.include_outline,
            outline_format=generate_data.outline_format
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating project content"
        ) from e
