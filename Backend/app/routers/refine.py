from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.auth_service import AuthService, get_current_user_dep
from ..services.section_service import SectionService

router = APIRouter(prefix="/projects/{project_id}/sections/{section_id}/refine", tags=["refine"])

@router.post(
    "/",
    response_model=schemas.SectionResponse,
    summary="Refine section content using AI"
)
async def refine_section_content(
    project_id: UUID,
    section_id: UUID,
    refine_data: schemas.SectionRefineRequest,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Refine the content of a section using AI based on the provided instructions.
    
    - **refine_instruction**: Detailed instructions for refining the content
    - **prompt**: Additional context or prompt for the refinement
    - **preserve_formatting**: Whether to preserve the existing formatting (default: True)
    - **temperature**: Controls randomness (0.0 to 1.0)
    - **max_tokens**: Maximum number of tokens to generate
    """
    section_service = SectionService(db)
    try:
        return await section_service.refine_section_content(
            section_id=section_id,
            project_id=project_id,
            user_id=current_user.id,
            refine_data=refine_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while refining the section content"
        ) from e

@router.post(
    "/generate",
    response_model=schemas.SectionResponse,
    summary="Generate content for a section using AI"
)
async def generate_section_content(
    project_id: UUID,
    section_id: UUID,
    generate_data: schemas.SectionGenerateRequest,
    current_user: models.User = Depends(get_current_user_dep),
    db: Session = Depends(get_db)
) -> Any:
    """
    Generate content for a section using AI.
    
    - **prompt**: The prompt for content generation
    - **temperature**: Controls randomness (0.0 to 1.0)
    - **max_tokens**: Maximum number of tokens to generate
    """
    section_service = SectionService(db)
    try:
        return await section_service.generate_section_content(
            section_id=section_id,
            project_id=project_id,
            user_id=current_user.id,
            prompt=generate_data.prompt,
            temperature=generate_data.temperature,
            max_tokens=generate_data.max_tokens
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating section content"
        ) from e
