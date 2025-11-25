import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)  # 'docx' or 'pptx'
    topic_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="projects")
    sections = relationship("Section", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.title} ({self.doc_type})>"

    @property
    def section_count(self):
        return len(self.sections)

# Add the relationship to User model
from app.models.user import User
User.projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
