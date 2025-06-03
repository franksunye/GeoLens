"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_auth_service
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse
)
from app.schemas.user import (
    UserCreate, UserResponse, UserUpdate, UserPasswordUpdate,
    UserPasswordReset, UserPasswordResetConfirm, UserProfile
)
from app.schemas.common import APIResponse
from app.services.auth import AuthService


router = APIRouter()


@router.post("/register", response_model=APIResponse[UserResponse])
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register new user.
    
    Args:
        user_data: User registration data
        auth_service: Authentication service
        
    Returns:
        APIResponse[UserResponse]: Created user information
    """
    user = auth_service.create_user(user_data)
    
    return APIResponse(
        data=UserResponse.from_orm(user),
        message="User registered successfully"
    )


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    User login.
    
    Args:
        login_data: Login credentials
        auth_service: Authentication service
        
    Returns:
        APIResponse[LoginResponse]: Login response with tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = auth_service.authenticate_user(
        login_data.email, 
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    tokens = auth_service.create_tokens(user)
    
    return APIResponse(
        data=LoginResponse(
            **tokens,
            user=UserResponse.from_orm(user)
        ),
        message="Login successful"
    )


@router.post("/refresh", response_model=APIResponse[RefreshTokenResponse])
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token.
    
    Args:
        refresh_data: Refresh token data
        auth_service: Authentication service
        
    Returns:
        APIResponse[RefreshTokenResponse]: New access token
    """
    tokens = auth_service.refresh_access_token(refresh_data.refresh_token)
    
    return APIResponse(
        data=RefreshTokenResponse(**tokens),
        message="Token refreshed successfully"
    )


@router.get("/me", response_model=APIResponse[UserProfile])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        APIResponse[UserProfile]: User profile information
    """
    return APIResponse(
        data=UserProfile.from_orm(current_user),
        message="User profile retrieved successfully"
    )


@router.put("/me", response_model=APIResponse[UserProfile])
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update current user profile.
    
    Args:
        user_data: User update data
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        APIResponse[UserProfile]: Updated user profile
    """
    updated_user = auth_service.update_user(current_user, user_data)
    
    return APIResponse(
        data=UserProfile.from_orm(updated_user),
        message="User profile updated successfully"
    )


@router.post("/change-password", response_model=APIResponse[dict])
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change user password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        APIResponse[dict]: Success message
    """
    auth_service.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    
    return APIResponse(
        data={"success": True},
        message="Password changed successfully"
    )


@router.post("/reset-password", response_model=APIResponse[dict])
async def reset_password(
    reset_data: UserPasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request password reset.
    
    Args:
        reset_data: Password reset request data
        auth_service: Authentication service
        
    Returns:
        APIResponse[dict]: Reset token (in production, send via email)
    """
    reset_token = auth_service.reset_password(reset_data.email)
    
    # In production, send this token via email instead of returning it
    return APIResponse(
        data={"reset_token": reset_token},
        message="Password reset token generated"
    )


@router.post("/reset-password/confirm", response_model=APIResponse[dict])
async def confirm_password_reset(
    reset_data: UserPasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Confirm password reset.
    
    Args:
        reset_data: Password reset confirmation data
        auth_service: Authentication service
        
    Returns:
        APIResponse[dict]: Success message
    """
    auth_service.confirm_password_reset(
        reset_data.token,
        reset_data.new_password
    )
    
    return APIResponse(
        data={"success": True},
        message="Password reset successfully"
    )
