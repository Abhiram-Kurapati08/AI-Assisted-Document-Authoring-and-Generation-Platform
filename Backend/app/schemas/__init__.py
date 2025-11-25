# Base schemas for common fields
from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field
from uuid import UUID

# Generic type for pagination responses
T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

class PaginatedResponse(BaseResponse[T], Generic[T]):
    total: int
    page: int
    size: int
    items: list[T]

# Common fields
class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None

class UUIDMixin(BaseModel):
    id: UUID

# Common query params
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Items per page")

# Import specific schemas to expose them
from .auth import Token, TokenData, UserBase, UserCreate, UserLogin, UserResponse, UserInDB
from .project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectListParams,
    ProjectGenerateRequest,
)
from .section import (
    SectionBase,
    SectionCreate,
    SectionUpdate,
    SectionResponse,
    SectionListResponse,
    SectionListParams,
    SectionGenerateRequest,
    SectionRefineRequest,
    SectionContentUpdate,
)
from .revision import RevisionCreate, RevisionResponse
from .comment import CommentCreate, CommentResponse
from .feedback import FeedbackCreate, FeedbackResponse
from .export import (
    ExportFormat,
    DocumentStyle,
    PresentationStyle,
    ExportRequest,
    ExportResponse,
    ExportStatusResponse,
)
