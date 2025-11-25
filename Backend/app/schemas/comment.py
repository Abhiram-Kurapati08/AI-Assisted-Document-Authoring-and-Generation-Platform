from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from ..schemas import TimestampMixin, UUIDMixin, PaginationParams

class CommentBase(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    pass

class CommentResponse(CommentBase, UUIDMixin):
    section_id: UUID
    user_id: UUID
    created_at: datetime
    user_email: str
    
    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    items: List[CommentResponse]
    total: int
    page: int
    size: int

class CommentListParams(PaginationParams):
    user_id: Optional[UUID] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"  # 'asc' or 'desc'
