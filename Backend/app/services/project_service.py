from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from .. import models, schemas
from ..llm.provider import LLMProvider, get_llm_provider

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        try:
            self.llm_provider: Optional[LLMProvider] = get_llm_provider()
        except Exception:
            self.llm_provider = None

    async def create_project(
        self, 
        project_data: schemas.ProjectCreate, 
        user_id: UUID
    ) -> models.Project:
        """Create a new project."""
        # Create project
        db_project = models.Project(
            id=uuid4(),
            user_id=user_id,
            title=project_data.title,
            doc_type=project_data.doc_type,
            topic_prompt=project_data.topic_prompt
        )
        
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        
        return db_project

    async def list_projects(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        doc_type: Optional[str] = None
    ) -> Tuple[List[models.Project], int]:
        """List projects with optional filtering and pagination."""
        query = self.db.query(models.Project).filter(
            models.Project.user_id == user_id
        )
        
        # Apply filters
        if search:
            query = query.filter(
                models.Project.title.ilike(f"%{search}%")
            )
        
        if doc_type:
            query = query.filter(
                models.Project.doc_type == doc_type
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        projects = query.offset(skip).limit(limit).all()
        
        return projects, total

    async def get_project(
        self, 
        project_id: UUID, 
        user_id: UUID
    ) -> Optional[models.Project]:
        """Get a project by ID if it belongs to the user."""
        return self.db.query(models.Project).filter(
            and_(
                models.Project.id == project_id,
                models.Project.user_id == user_id
            )
        ).first()

    async def update_project(
        self,
        project_id: UUID,
        user_id: UUID,
        update_data: schemas.ProjectUpdate
    ) -> Optional[models.Project]:
        """Update a project's details."""
        db_project = await self.get_project(project_id, user_id)
        if not db_project:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            return db_project
            
        for field, value in update_dict.items():
            setattr(db_project, field, value)
            
        db_project.updated_at = datetime.utcnow()
        
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        
        return db_project

    async def delete_project(
        self, 
        project_id: UUID, 
        user_id: UUID
    ) -> bool:
        """Delete a project and all its related data."""
        db_project = await self.get_project(project_id, user_id)
        if not db_project:
            return False
            
        self.db.delete(db_project)
        self.db.commit()
        return True

    async def generate_initial_content(
        self,
        project_id: UUID,
        user_id: UUID,
        num_sections: int = 5,
        include_outline: bool = True,
        outline_format: Optional[str] = None
    ) -> List[models.Section]:
        """Generate initial content sections for a project using AI."""
        # Verify project exists and belongs to user
        project = await self.get_project(project_id, user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if not self.llm_provider:
             raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM provider is not configured. Cannot generate content."
            )
        
        # Generate outline if requested
        try:
            outline = None
            if include_outline:
                outline = await self._generate_outline(
                    project=project,
                    num_sections=num_sections,
                    outline_format=outline_format
                )
            
            # Generate content for each section
            sections = []
            for i in range(num_sections):
                section_title = f"Section {i+1}" if not outline else outline[i]
                
                # Generate content using LLM
                prompt = self._build_section_prompt(
                    project=project,
                    section_title=section_title,
                    section_number=i+1,
                    total_sections=num_sections
                )
                
                content = await self.llm_provider.generate_text(
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                # Create section
                section = models.Section(
                    id=uuid4(),
                    project_id=project_id,
                    title=section_title,
                    content=content,
                    idx=i,
                    initial_generated=True
                )
                
                self.db.add(section)
                sections.append(section)
            
            # Update project timestamp
            project.updated_at = datetime.utcnow()
            self.db.add(project)
            self.db.commit()
            
            # Refresh all sections
            for section in sections:
                self.db.refresh(section)
                
            return sections
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating content: {str(e)}"
            )

    async def _generate_outline(
        self,
        project: models.Project,
        num_sections: int,
        outline_format: Optional[str] = None
    ) -> List[str]:
        """Generate an outline for the project."""
        prompt = f"""
        Generate a detailed outline for a {project.doc_type.upper()} document 
        about "{project.topic_prompt or project.title}".
        
        The outline should have {num_sections} main sections.
        """
        
        if outline_format:
            prompt += f"\nUse the following format for the outline: {outline_format}"
        
        prompt += "\n\nReturn just the outline with each section title on a new line."
        
        response = await self.llm_provider.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.5
        )
        
        # Parse the response into a list of section titles
        section_titles = [
            line.strip() 
            for line in response.split('\n') 
            if line.strip()
        ]
        
        # Ensure we have the correct number of sections
        if len(section_titles) < num_sections:
            # Pad with default section titles if needed
            for i in range(len(section_titles), num_sections):
                section_titles.append(f"Section {i+1}")
        else:
            section_titles = section_titles[:num_sections]
            
        return section_titles

    def _build_section_prompt(
        self,
        project: models.Project,
        section_title: str,
        section_number: int,
        total_sections: int
    ) -> str:
        """Build a prompt for generating section content."""
        prompt = f"""
        Write a detailed section for a {project.doc_type.upper()} document.
        
        Document Topic: {project.topic_prompt or project.title}
        Section Title: {section_title}
        Section {section_number} of {total_sections}
        
        Write comprehensive content for this section. Include relevant details, 
        examples, and explanations as appropriate for the topic.
        """
        
        if project.doc_type == "pptx":
            prompt += """
            Since this is for a presentation, structure the content in a way that 
            would work well on slides. Use bullet points and keep paragraphs concise.
            """
        
        return prompt.strip()
