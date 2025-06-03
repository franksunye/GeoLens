"""
Project management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetail,
    ProjectList, ProjectStats
)
from app.schemas.common import APIResponse, PaginationParams, PaginatedResponse
from app.services.project import ProjectService


router = APIRouter()


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """Get project service instance."""
    return ProjectService(db)


@router.post("/", response_model=APIResponse[ProjectResponse], status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Create new project.
    
    Args:
        project_data: Project creation data
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[ProjectResponse]: Created project information
    """
    project = project_service.create_project(project_data, str(current_user.id))
    
    return APIResponse(
        data=ProjectResponse.from_orm(project),
        message="Project created successfully"
    )


@router.get("/", response_model=APIResponse[PaginatedResponse[ProjectResponse]])
async def get_projects(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get user projects with pagination and filtering.
    
    Args:
        page: Page number
        per_page: Items per page
        is_active: Filter by active status
        search: Search term
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[PaginatedResponse[ProjectResponse]]: Paginated projects
    """
    pagination = PaginationParams(page=page, per_page=per_page)
    
    projects, total = project_service.get_user_projects(
        str(current_user.id),
        pagination,
        is_active=is_active,
        search=search
    )
    
    project_responses = [ProjectResponse.from_orm(p) for p in projects]
    
    paginated_response = PaginatedResponse.create(
        items=project_responses,
        total=total,
        page=page,
        per_page=per_page
    )
    
    return APIResponse(
        data=paginated_response,
        message="Projects retrieved successfully"
    )


@router.get("/stats", response_model=APIResponse[ProjectStats])
async def get_project_stats(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get project statistics for current user.
    
    Args:
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[ProjectStats]: Project statistics
    """
    stats = project_service.get_project_stats(str(current_user.id))
    
    return APIResponse(
        data=ProjectStats(**stats),
        message="Project statistics retrieved successfully"
    )


@router.get("/{project_id}", response_model=APIResponse[ProjectDetail])
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get project by ID.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[ProjectDetail]: Project details
        
    Raises:
        HTTPException: If project not found
    """
    project = project_service.get_project_by_id(
        project_id, 
        str(current_user.id)
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return APIResponse(
        data=ProjectDetail.from_orm(project),
        message="Project retrieved successfully"
    )


@router.put("/{project_id}", response_model=APIResponse[ProjectResponse])
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Update project.
    
    Args:
        project_id: Project ID
        project_data: Project update data
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[ProjectResponse]: Updated project
        
    Raises:
        HTTPException: If project not found
    """
    project = project_service.get_project_by_id(
        project_id, 
        str(current_user.id)
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    updated_project = project_service.update_project(project, project_data)
    
    return APIResponse(
        data=ProjectResponse.from_orm(updated_project),
        message="Project updated successfully"
    )


@router.delete("/{project_id}", response_model=APIResponse[dict])
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Delete project.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[dict]: Success message
        
    Raises:
        HTTPException: If project not found
    """
    project = project_service.get_project_by_id(
        project_id, 
        str(current_user.id)
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project_service.delete_project(project)
    
    return APIResponse(
        data={"success": True},
        message="Project deleted successfully"
    )


@router.post("/{project_id}/toggle", response_model=APIResponse[ProjectResponse])
async def toggle_project_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Toggle project active status.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[ProjectResponse]: Updated project
        
    Raises:
        HTTPException: If project not found
    """
    project = project_service.get_project_by_id(
        project_id, 
        str(current_user.id)
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    updated_project = project_service.toggle_project_status(project)
    
    return APIResponse(
        data=ProjectResponse.from_orm(updated_project),
        message=f"Project {'activated' if updated_project.is_active else 'deactivated'} successfully"
    )


@router.post("/{project_id}/keywords", response_model=APIResponse[ProjectResponse])
async def add_keywords(
    project_id: str,
    keywords: List[str],
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Add keywords to project.
    
    Args:
        project_id: Project ID
        keywords: List of keywords to add
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[ProjectResponse]: Updated project
        
    Raises:
        HTTPException: If project not found
    """
    project = project_service.get_project_by_id(
        project_id, 
        str(current_user.id)
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    updated_project = project_service.add_keywords(project, keywords)
    
    return APIResponse(
        data=ProjectResponse.from_orm(updated_project),
        message="Keywords added successfully"
    )


@router.delete("/{project_id}/keywords", response_model=APIResponse[ProjectResponse])
async def remove_keywords(
    project_id: str,
    keywords: List[str],
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Remove keywords from project.
    
    Args:
        project_id: Project ID
        keywords: List of keywords to remove
        current_user: Current authenticated user
        project_service: Project service
        
    Returns:
        APIResponse[ProjectResponse]: Updated project
        
    Raises:
        HTTPException: If project not found
    """
    project = project_service.get_project_by_id(
        project_id, 
        str(current_user.id)
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    updated_project = project_service.remove_keywords(project, keywords)
    
    return APIResponse(
        data=ProjectResponse.from_orm(updated_project),
        message="Keywords removed successfully"
    )
