from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ExportFormat(str, Enum):
    DOCX = "docx"
    PPTX = "pptx"
    PDF = "pdf"
    TXT = "txt"

class DocumentStyle(BaseModel):
    font_name: str = "Arial"
    font_size: int = Field(11, ge=8, le=72)
    line_spacing: float = Field(1.15, ge=1.0, le=3.0)
    margin_top: float = Field(1.0, ge=0.5, le=2.0)
    margin_bottom: float = Field(1.0, ge=0.5, le=2.0)
    margin_left: float = Field(1.0, ge=0.5, le=2.0)
    margin_right: float = Field(1.0, ge=0.5, le=2.0)

class PresentationStyle(BaseModel):
    theme: str = "OFFICE"
    title_font_size: int = Field(44, ge=24, le=72)
    content_font_size: int = Field(32, ge=12, le=48)
    include_speaker_notes: bool = True

class ExportRequest(BaseModel):
    format: ExportFormat
    include_comments: bool = False
    include_revision_history: bool = False
    include_metadata: bool = True
    document_style: Optional[DocumentStyle] = None
    presentation_style: Optional[PresentationStyle] = None
    custom_styles: Optional[Dict[str, Any]] = None

class ExportResponse(BaseModel):
    export_id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    download_url: Optional[str] = None
    file_size: Optional[int] = None  # in bytes
    created_at: str
    expires_at: Optional[str] = None

class ExportStatusResponse(BaseModel):
    status: str
    progress: Optional[int] = Field(None, ge=0, le=100)  # percentage
    message: Optional[str] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
