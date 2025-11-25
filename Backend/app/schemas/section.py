from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from ..schemas import TimestampMixin, UUIDMixin, PaginationParams

class SectionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    idx: int = Field(..., ge=0, description="Position of the section in the document")

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    idx: Optional[int] = Field(None, ge=0)

class SectionResponse(SectionBase, UUIDMixin, TimestampMixin):
    project_id: UUID
    initial_generated: bool = False
    revision_count: int = 0
    comment_count: int = 0
    has_feedback: bool = False
    
    class Config:
        from_attributes = True

class SectionListResponse(BaseModel):
    items: List[SectionResponse]
    total: int
    page: int
    size: int

class SectionListParams(PaginationParams):
    search: Optional[str] = None
    initial_only: bool = False

class SectionGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=1000, description="Prompt for content generation")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Creativity level (0.0 to 1.0)")
    max_tokens: int = Field(1000, ge=100, le=4000, description="Maximum number of tokens to generate")

class SectionRefineRequest(SectionGenerateRequest):
    refine_instruction: str = Field(..., min_length=10, max_length=1000, 
                                  description="Instructions for refining the content")
    preserve_formatting: bool = True

class SectionContentUpdate(BaseModel):
    content: str = Field(..., min_length=1, description="Updated section content")
