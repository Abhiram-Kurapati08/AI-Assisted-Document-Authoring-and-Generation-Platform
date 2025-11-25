import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    idx = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    initial_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="sections")
    revisions = relationship("Revision", back_populates="section", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="section", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="section", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Section {self.title} (Project: {self.project_id})>"

# Import Project here to avoid circular imports
from app.models.project import Project
