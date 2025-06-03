"""
Dependency injection for FastAPI.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.services.auth import AuthService


# Security scheme
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Get current user ID from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        str: User ID
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    user_id = verify_token(token, token_type="access")
    return user_id


def get_current_user(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> User:
    """
    Get current authenticated user.
    
    Args:
        db: Database session
        user_id: Current user ID
        
    Returns:
        User: Current user object
        
    Raises:
        HTTPException: If user not found
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        User: Active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser.
    
    Args:
        current_user: Current user
        
    Returns:
        User: Superuser
        
    Raises:
        HTTPException: If user is not superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    
    Args:
        db: Database session
        credentials: Optional HTTP authorization credentials
        
    Returns:
        User or None: Current user if authenticated
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_id = verify_token(token, token_type="access")
        
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id)
        
        if user and user.is_active:
            return user
    except HTTPException:
        pass
    
    return None


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    Get authentication service.
    
    Args:
        db: Database session
        
    Returns:
        AuthService: Authentication service instance
    """
    return AuthService(db)
