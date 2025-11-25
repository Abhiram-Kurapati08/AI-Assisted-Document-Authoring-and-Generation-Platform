from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from ..schemas import TimestampMixin, UUIDMixin, PaginationParams

class RevisionBase(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    generated_content: str = Field(..., min_length=1)

class RevisionCreate(RevisionBase):
    pass

class RevisionResponse(RevisionBase, UUIDMixin):
    section_id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class RevisionListResponse(BaseModel):
    items: List[RevisionResponse]
    total: int
    page: int
    size: int

class RevisionListParams(PaginationParams):
    user_id: Optional[UUID] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"  # 'asc' or 'desc'
