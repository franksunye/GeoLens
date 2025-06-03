"""
User Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import uuid


# Base schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check for at least one digit
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        
        # Check for at least one letter
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    """Schema for password updates."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator("new_password")
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        
        return v


class UserPasswordReset(BaseModel):
    """Schema for password reset."""
    email: EmailStr


class UserPasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


# Response schemas
class UserResponse(UserBase):
    """Schema for user response."""
    id: uuid.UUID
    email_verified: bool
    subscription_plan: str
    subscription_expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Schema for user profile with additional fields."""
    avatar_url: Optional[str]
    bio: Optional[str]
    is_premium: bool
    
    class Config:
        from_attributes = True


class UserSummary(BaseModel):
    """Schema for user summary (minimal info)."""
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str]
    avatar_url: Optional[str]
    
    class Config:
        from_attributes = True
