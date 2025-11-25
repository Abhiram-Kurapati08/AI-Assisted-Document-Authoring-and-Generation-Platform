from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from ..schemas import TimestampMixin, UUIDMixin, PaginationParams

class DocumentType(str, Enum):
    DOCX = "docx"
    PPTX = "pptx"

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    doc_type: DocumentType
    topic_prompt: Optional[str] = Field(None, max_length=1000)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    topic_prompt: Optional[str] = Field(None, max_length=1000)

class ProjectResponse(ProjectBase, UUIDMixin, TimestampMixin):
    user_id: UUID
    section_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    size: int

class ProjectListParams(PaginationParams):
    search: Optional[str] = None
    doc_type: Optional[DocumentType] = None

class ProjectGenerateRequest(BaseModel):
    num_sections: int = Field(5, ge=1, le=20, description="Number of sections to generate")
    include_outline: bool = True
    outline_format: Optional[str] = Field(
        None,
        description="Optional format for the outline (e.g., 'I. A. 1.' or '1.1, 1.2, 2.1')",
        max_length=50
    )
