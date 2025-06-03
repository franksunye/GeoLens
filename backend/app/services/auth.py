"""
Authentication service for user management and authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_password_reset_token,
    verify_password_reset_token
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import settings


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None: User object if found
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None: User object if found
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            User: Created user object
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=hashed_password,
            is_active=user_data.is_active
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User or None: User object if authentication successful
        """
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.update_last_login()
        self.db.commit()
        
        return user
    
    def update_user(self, user: User, user_data: UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            user: User object to update
            user_data: Update data
            
        Returns:
            User: Updated user object
        """
        update_data = user_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(
        self, 
        user: User, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            user: User object
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            HTTPException: If current password is incorrect
        """
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        return True
    
    def reset_password(self, email: str) -> str:
        """
        Generate password reset token.
        
        Args:
            email: User email
            
        Returns:
            str: Password reset token
            
        Raises:
            HTTPException: If user not found
        """
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return generate_password_reset_token(email)
    
    def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """
        Confirm password reset with token.
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            bool: True if password reset successful
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        email = verify_password_reset_token(token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        return True
    
    def create_tokens(self, user: User) -> dict:
        """
        Create access and refresh tokens for user.
        
        Args:
            user: User object
            
        Returns:
            dict: Token information
        """
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            dict: New token information
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        user_id = verify_token(refresh_token, token_type="refresh")
        user = self.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        access_token = create_access_token(subject=str(user.id))
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
