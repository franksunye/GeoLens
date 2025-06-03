"""
Common Pydantic schemas for API responses.
"""
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Generic API response schema."""
    success: bool = True
    data: Optional[DataT] = None
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorDetail(BaseModel):
    """Error detail schema."""
    code: str
    message: str
    details: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: ErrorDetail
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters schema."""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=10, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated response schema."""
    items: List[DataT]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[DataT],
        total: int,
        page: int,
        per_page: int
    ) -> "PaginatedResponse[DataT]":
        """Create paginated response."""
        pages = (total + per_page - 1) // per_page
        
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


class HealthCheck(BaseModel):
    """Health check response schema."""
    status: str = "healthy"
    version: str
    uptime: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict = Field(default_factory=dict)
