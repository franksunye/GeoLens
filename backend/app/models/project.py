"""
Project model definition.
"""
from typing import TYPE_CHECKING, List
from sqlalchemy import (
    Boolean, Column, DateTime, String, Text, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.user import GUID

if TYPE_CHECKING:
    from app.models.user import User


class Project(Base):
    """Project model for brand monitoring."""
    
    __tablename__ = "projects"
    
    # Primary key
    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Foreign key
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Basic information
    name = Column(String(100), nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configuration
    industry = Column(String(50), nullable=True)
    target_keywords = Column(JSON, nullable=True, default=[])
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, domain={self.domain})>"
    
    @property
    def keywords_count(self) -> int:
        """Get number of target keywords."""
        return len(self.target_keywords) if self.target_keywords else 0
    
    def add_keyword(self, keyword: str) -> None:
        """Add a target keyword."""
        if not self.target_keywords:
            self.target_keywords = []
        
        if keyword not in self.target_keywords:
            self.target_keywords.append(keyword)
    
    def remove_keyword(self, keyword: str) -> None:
        """Remove a target keyword."""
        if self.target_keywords and keyword in self.target_keywords:
            self.target_keywords.remove(keyword)
    
    def update_keywords(self, keywords: List[str]) -> None:
        """Update target keywords list."""
        self.target_keywords = list(set(keywords))  # Remove duplicates
