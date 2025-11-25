from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from ..schemas import UUIDMixin

class FeedbackBase(BaseModel):
    liked: bool

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase, UUIDMixin):
    section_id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class FeedbackStatsResponse(BaseModel):
    section_id: UUID
    total_likes: int
    total_dislikes: int
    user_feedback: Optional[bool] = None
    
    class Config:
        from_attributes = True
