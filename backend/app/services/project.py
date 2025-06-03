"""
Project service for project management operations.
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.common import PaginationParams


class ProjectService:
    """Project management service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_project_by_id(self, project_id: str, user_id: str) -> Optional[Project]:
        """
        Get project by ID for specific user.
        
        Args:
            project_id: Project ID
            user_id: User ID
            
        Returns:
            Project or None: Project object if found and owned by user
        """
        return self.db.query(Project).filter(
            and_(
                Project.id == project_id,
                Project.user_id == user_id
            )
        ).first()
    
    def get_project_by_domain(self, domain: str, user_id: str) -> Optional[Project]:
        """
        Get project by domain for specific user.
        
        Args:
            domain: Project domain
            user_id: User ID
            
        Returns:
            Project or None: Project object if found
        """
        return self.db.query(Project).filter(
            and_(
                Project.domain == domain.lower(),
                Project.user_id == user_id
            )
        ).first()
    
    def create_project(self, project_data: ProjectCreate, user_id: str) -> Project:
        """
        Create new project.
        
        Args:
            project_data: Project creation data
            user_id: Owner user ID
            
        Returns:
            Project: Created project object
            
        Raises:
            HTTPException: If domain already exists for user
        """
        # Check if domain already exists for this user
        existing_project = self.get_project_by_domain(
            project_data.domain, 
            user_id
        )
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project with this domain already exists"
            )
        
        # Create new project
        db_project = Project(
            user_id=user_id,
            name=project_data.name,
            domain=project_data.domain.lower(),
            description=project_data.description,
            industry=project_data.industry,
            target_keywords=project_data.target_keywords
        )
        
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        
        return db_project
    
    def update_project(
        self, 
        project: Project, 
        project_data: ProjectUpdate
    ) -> Project:
        """
        Update project information.
        
        Args:
            project: Project object to update
            project_data: Update data
            
        Returns:
            Project: Updated project object
        """
        update_data = project_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def delete_project(self, project: Project) -> bool:
        """
        Delete project.
        
        Args:
            project: Project object to delete
            
        Returns:
            bool: True if deleted successfully
        """
        self.db.delete(project)
        self.db.commit()
        return True
    
    def get_user_projects(
        self, 
        user_id: str, 
        pagination: PaginationParams,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Project], int]:
        """
        Get user projects with pagination and filtering.
        
        Args:
            user_id: User ID
            pagination: Pagination parameters
            is_active: Filter by active status
            search: Search term for name or domain
            
        Returns:
            Tuple[List[Project], int]: Projects and total count
        """
        query = self.db.query(Project).filter(Project.user_id == user_id)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Project.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Project.name.ilike(search_term) |
                Project.domain.ilike(search_term)
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        projects = query.order_by(
            Project.created_at.desc()
        ).offset(pagination.offset).limit(pagination.per_page).all()
        
        return projects, total
    
    def get_project_stats(self, user_id: str) -> dict:
        """
        Get project statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Project statistics
        """
        # Get basic counts
        total_projects = self.db.query(Project).filter(
            Project.user_id == user_id
        ).count()
        
        active_projects = self.db.query(Project).filter(
            and_(
                Project.user_id == user_id,
                Project.is_active == True
            )
        ).count()
        
        inactive_projects = total_projects - active_projects
        
        # Get keyword statistics (compatible with SQLite and PostgreSQL)
        projects_with_keywords = self.db.query(Project).filter(
            and_(
                Project.user_id == user_id,
                Project.target_keywords.isnot(None)
            )
        ).all()

        total_keywords = sum(
            len(project.target_keywords) if project.target_keywords else 0
            for project in projects_with_keywords
        )
        avg_keywords = (
            total_keywords / total_projects 
            if total_projects > 0 
            else 0
        )
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "inactive_projects": inactive_projects,
            "total_keywords": total_keywords,
            "avg_keywords_per_project": round(avg_keywords, 2)
        }
    
    def toggle_project_status(self, project: Project) -> Project:
        """
        Toggle project active status.
        
        Args:
            project: Project object
            
        Returns:
            Project: Updated project object
        """
        project.is_active = not project.is_active
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def add_keywords(self, project: Project, keywords: List[str]) -> Project:
        """
        Add keywords to project.
        
        Args:
            project: Project object
            keywords: List of keywords to add
            
        Returns:
            Project: Updated project object
        """
        current_keywords = project.target_keywords or []
        new_keywords = list(set(current_keywords + keywords))
        
        if len(new_keywords) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 keywords allowed per project"
            )
        
        project.target_keywords = new_keywords
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def remove_keywords(self, project: Project, keywords: List[str]) -> Project:
        """
        Remove keywords from project.
        
        Args:
            project: Project object
            keywords: List of keywords to remove
            
        Returns:
            Project: Updated project object
        """
        current_keywords = project.target_keywords or []
        new_keywords = [kw for kw in current_keywords if kw not in keywords]
        
        project.target_keywords = new_keywords
        self.db.commit()
        self.db.refresh(project)
        
        return project
