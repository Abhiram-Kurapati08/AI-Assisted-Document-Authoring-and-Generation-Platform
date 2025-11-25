import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class Revision(Base):
    __tablename__ = "revisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    prompt = Column(Text, nullable=False)
    generated_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    section = relationship("Section", back_populates="revisions")
    user = relationship("User")

    def __repr__(self):
        return f"<Revision {self.id} (Section: {self.section_id})>"

# Import models to avoid circular imports
from app.models.section import Section
from app.models.user import User
