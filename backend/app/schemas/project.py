"""
Project Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import uuid

from app.schemas.user import UserSummary


# Base schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=2, max_length=100)
    domain: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = Field(None, max_length=50)
    target_keywords: List[str] = Field(default_factory=list)
    
    @validator("domain")
    def validate_domain(cls, v):
        """Validate domain format."""
        import re
        
        # Basic domain validation
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, v.lower()):
            raise ValueError("Invalid domain format")
        
        return v.lower()
    
    @validator("target_keywords")
    def validate_keywords(cls, v):
        """Validate target keywords."""
        if len(v) > 20:
            raise ValueError("Maximum 20 target keywords allowed")
        
        # Remove duplicates and empty strings
        keywords = [kw.strip() for kw in v if kw.strip()]
        
        # Validate each keyword
        for keyword in keywords:
            if len(keyword) > 50:
                raise ValueError("Each keyword must be less than 50 characters")
        
        return keywords


class ProjectCreate(ProjectBase):
    """Schema for project creation."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for project updates."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = Field(None, max_length=50)
    target_keywords: Optional[List[str]] = None
    is_active: Optional[bool] = None
    
    @validator("target_keywords")
    def validate_keywords(cls, v):
        """Validate target keywords."""
        if v is None:
            return v
        
        if len(v) > 20:
            raise ValueError("Maximum 20 target keywords allowed")
        
        # Remove duplicates and empty strings
        keywords = [kw.strip() for kw in v if kw.strip()]
        
        # Validate each keyword
        for keyword in keywords:
            if len(keyword) > 50:
                raise ValueError("Each keyword must be less than 50 characters")
        
        return keywords


# Response schemas
class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    keywords_count: int
    
    class Config:
        from_attributes = True


class ProjectDetail(ProjectResponse):
    """Schema for detailed project response."""
    owner: UserSummary
    
    class Config:
        from_attributes = True


class ProjectSummary(BaseModel):
    """Schema for project summary (minimal info)."""
    id: uuid.UUID
    name: str
    domain: str
    is_active: bool
    keywords_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectList(BaseModel):
    """Schema for project list response."""
    projects: List[ProjectSummary]
    total: int
    page: int
    per_page: int
    pages: int


class ProjectStats(BaseModel):
    """Schema for project statistics."""
    total_projects: int
    active_projects: int
    inactive_projects: int
    total_keywords: int
    avg_keywords_per_project: float
