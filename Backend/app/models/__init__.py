# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .project import Project
from .section import Section
from .revision import Revision
from .comment import Comment
from .feedback import Feedback
from ..database import Base

# Make models available for direct import from app.models
__all__ = [
    'Base',
    'User',
    'Project',
    'Section',
    'Revision',
    'Comment',
    'Feedback'
]
