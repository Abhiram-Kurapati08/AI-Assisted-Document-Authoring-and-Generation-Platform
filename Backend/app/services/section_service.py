from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from .. import models, schemas
from ..llm.provider import get_llm_provider

class SectionService:
    def __init__(self, db: Session):
        self.db = db
        try:
            self.llm_provider = get_llm_provider()
        except Exception:
            self.llm_provider = None

    async def create_section(
        self,
        project_id: UUID,
        user_id: UUID,
        section_data: schemas.SectionBase
    ) -> models.Section:
        """Create a new section in a project."""
        # Verify project exists and belongs to user
        project = self.db.query(models.Project).filter(
            and_(
                models.Project.id == project_id,
                models.Project.user_id == user_id
            )
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Create section
        db_section = models.Section(
            id=uuid4(),
            project_id=project_id,
            title=section_data.title,
            content=section_data.content,
            idx=section_data.idx,
            initial_generated=False
        )
        
        self.db.add(db_section)
        self.db.commit()
        self.db.refresh(db_section)
        
        # Update project's updated_at timestamp
        project.updated_at = datetime.utcnow()
        self.db.add(project)
        self.db.commit()
        
        return db_section

    async def list_sections(
        self,
        project_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        initial_only: bool = False
    ) -> Tuple[List[models.Section], int]:
        """List sections in a project with optional filtering and pagination."""
        # Verify project exists and belongs to user
        project = self.db.query(models.Project).filter(
            and_(
                models.Project.id == project_id,
                models.Project.user_id == user_id
            )
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        query = self.db.query(models.Section).filter(
            models.Section.project_id == project_id
        )
        
        # Apply filters
        if search:
            search_filter = or_(
                models.Section.title.ilike(f"%{search}%"),
                models.Section.content.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if initial_only:
            query = query.filter(
                models.Section.initial_generated == True
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        sections = (
            query.order_by(models.Section.idx.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return sections, total

    async def get_section(
        self,
        section_id: UUID,
        project_id: UUID,
        user_id: UUID
    ) -> Optional[models.Section]:
        """Get a section by ID if it belongs to the user's project."""
        section = self.db.query(models.Section).join(
            models.Project,
            models.Section.project_id == models.Project.id
        ).filter(
            and_(
                models.Section.id == section_id,
                models.Section.project_id == project_id,
                models.Project.user_id == user_id
            )
        ).first()
        
        return section

    async def update_section(
        self,
        section_id: UUID,
        project_id: UUID,
        user_id: UUID,
        update_data: schemas.SectionUpdate
    ) -> Optional[models.Section]:
        """Update a section's details."""
        section = await self.get_section(section_id, project_id, user_id)
        if not section:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            return section
        
        # Update section fields
        for field, value in update_dict.items():
            setattr(section, field, value)
        
        section.updated_at = datetime.utcnow()
        
        # Update project's updated_at timestamp
        project = self.db.query(models.Project).get(project_id)
        if project:
            project.updated_at = datetime.utcnow()
            self.db.add(project)
        
        self.db.add(section)
        self.db.commit()
        self.db.refresh(section)
        
        return section

    async def delete_section(
        self,
        section_id: UUID,
        project_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a section."""
        section = await self.get_section(section_id, project_id, user_id)
        if not section:
            return False
        
        # Update project's updated_at timestamp
        project = self.db.query(models.Project).get(project_id)
        if project:
            project.updated_at = datetime.utcnow()
            self.db.add(project)
        
        self.db.delete(section)
        self.db.commit()
        return True

    async def generate_section_content(
        self,
        section_id: UUID,
        project_id: UUID,
        user_id: UUID,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> models.Section:
        """Generate content for a section using AI."""
        section = await self.get_section(section_id, project_id, user_id)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        
        if not self.llm_provider:
             raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM provider is not configured. Cannot generate content."
            )
        
        # Build the prompt for the LLM
        full_prompt = self._build_generation_prompt(section, prompt)
        
        try:
            # Generate content using the LLM provider
            generated_content = await self.llm_provider.generate_text(
                prompt=full_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Create a new revision
            revision = models.Revision(
                id=uuid4(),
                section_id=section_id,
                user_id=user_id,
                prompt=prompt,
                generated_content=generated_content
            )
            
            # Update section content
            section.content = generated_content
            section.updated_at = datetime.utcnow()
            
            # Update project's updated_at timestamp
            project = self.db.query(models.Project).get(project_id)
            if project:
                project.updated_at = datetime.utcnow()
                self.db.add(project)
            
            self.db.add(revision)
            self.db.add(section)
            self.db.commit()
            self.db.refresh(section)
            
            return section
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating content: {str(e)}"
            )
    
    def _build_generation_prompt(
        self,
        section: models.Section,
        user_prompt: str
    ) -> str:
        """Build a prompt for generating section content."""
        project = section.project
        
        prompt = f"""
        You are an AI assistant helping to write content for a document.
        
        Document Title: {project.title}
        Section Title: {section.title}
        
        User's instructions: {user_prompt}
        
        Current section content:
        {section.content or '(empty)'}
        
        Please generate high-quality content for this section based on the above information.
        """
        
        if project.doc_type == "pptx":
            prompt += """
            Note: This is for a presentation slide. Please keep the content concise and 
            suitable for bullet points. Use clear, impactful language.
            """
        
        return prompt.strip()
    
    async def refine_section_content(
        self,
        section_id: UUID,
        project_id: UUID,
        user_id: UUID,
        refine_data: schemas.SectionRefineRequest
    ) -> models.Section:
        """Refine a section's content using AI."""
        section = await self.get_section(section_id, project_id, user_id)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        
        if not self.llm_provider:
             raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM provider is not configured. Cannot refine content."
            )
        
        # Build the prompt for refinement
        prompt = self._build_refinement_prompt(section, refine_data)
        
        try:
            # Generate refined content using the LLM provider
            refined_content = await self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=refine_data.max_tokens,
                temperature=refine_data.temperature
            )
            
            # Create a new revision
            revision = models.Revision(
                id=uuid4(),
                section_id=section_id,
                user_id=user_id,
                prompt=refine_data.refine_instruction,
                generated_content=refined_content
            )
            
            # Update section content
            section.content = refined_content
            section.updated_at = datetime.utcnow()
            
            # Update project's updated_at timestamp
            project = self.db.query(models.Project).get(project_id)
            if project:
                project.updated_at = datetime.utcnow()
                self.db.add(project)
            
            self.db.add(revision)
            self.db.add(section)
            self.db.commit()
            self.db.refresh(section)
            
            return section
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error refining content: {str(e)}"
            )
    
    def _build_refinement_prompt(
        self,
        section: models.Section,
        refine_data: schemas.SectionRefineRequest
    ) -> str:
        """Build a prompt for refining section content."""
        project = section.project
        
        prompt = f"""
        You are an AI editor helping to refine content for a document.
        
        Document Title: {project.title}
        Section Title: {section.title}
        
        Current section content:
        {section.content or '(empty)'}
        
        Refinement instructions: {refine_data.refine_instruction}
        
        Please refine the content based on these instructions. """
        
        if refine_data.preserve_formatting:
            prompt += """
            Please preserve the existing formatting, markdown, and structure where possible.
            """
        
        if project.doc_type == "pptx":
            prompt += """
            Note: This is for a presentation slide. Please keep the content concise and 
            suitable for bullet points. Use clear, impactful language.
            """
        
        return prompt.strip()
