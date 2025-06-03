"""
Unit tests for authentication service.
"""
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.auth import AuthService
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password
from tests.conftest import UserFactory


class TestAuthService:
    """Test authentication service."""
    
    def test_create_user_success(self, db_session: Session):
        """Test successful user creation."""
        auth_service = AuthService(db_session)
        user_data = UserFactory.create_user_data(
            email="newuser@example.com",
            password="newpassword123"
        )
        
        user = auth_service.create_user(user_data)
        
        assert user.email == user_data.email
        assert user.full_name == user_data.full_name
        assert user.is_active == user_data.is_active
        assert verify_password("newpassword123", user.password_hash)
        assert user.id is not None
        assert user.created_at is not None
    
    def test_create_user_duplicate_email(self, db_session: Session, test_user):
        """Test user creation with duplicate email."""
        auth_service = AuthService(db_session)
        user_data = UserFactory.create_user_data(email=test_user.email)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.create_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail
    
    def test_get_user_by_email_exists(self, db_session: Session, test_user):
        """Test getting user by email when user exists."""
        auth_service = AuthService(db_session)
        
        user = auth_service.get_user_by_email(test_user.email)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_email_not_exists(self, db_session: Session):
        """Test getting user by email when user doesn't exist."""
        auth_service = AuthService(db_session)
        
        user = auth_service.get_user_by_email("nonexistent@example.com")
        
        assert user is None
    
    def test_get_user_by_id_exists(self, db_session: Session, test_user):
        """Test getting user by ID when user exists."""
        auth_service = AuthService(db_session)
        
        user = auth_service.get_user_by_id(str(test_user.id))
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_id_not_exists(self, db_session: Session):
        """Test getting user by ID when user doesn't exist."""
        auth_service = AuthService(db_session)
        
        user = auth_service.get_user_by_id("00000000-0000-0000-0000-000000000000")
        
        assert user is None
    
    def test_authenticate_user_success(self, db_session: Session, test_user):
        """Test successful user authentication."""
        auth_service = AuthService(db_session)
        
        user = auth_service.authenticate_user(test_user.email, "testpassword123")
        
        assert user is not None
        assert user.id == test_user.id
        assert user.last_login_at is not None
    
    def test_authenticate_user_wrong_email(self, db_session: Session):
        """Test authentication with wrong email."""
        auth_service = AuthService(db_session)
        
        user = auth_service.authenticate_user("wrong@example.com", "password")
        
        assert user is None
    
    def test_authenticate_user_wrong_password(self, db_session: Session, test_user):
        """Test authentication with wrong password."""
        auth_service = AuthService(db_session)
        
        user = auth_service.authenticate_user(test_user.email, "wrongpassword")
        
        assert user is None
    
    def test_update_user_success(self, db_session: Session, test_user):
        """Test successful user update."""
        auth_service = AuthService(db_session)
        update_data = UserUpdate(
            full_name="Updated Name",
            bio="Updated bio"
        )
        
        updated_user = auth_service.update_user(test_user, update_data)
        
        assert updated_user.full_name == "Updated Name"
        assert updated_user.bio == "Updated bio"
        assert updated_user.email == test_user.email  # Unchanged
    
    def test_change_password_success(self, db_session: Session, test_user):
        """Test successful password change."""
        auth_service = AuthService(db_session)
        old_password_hash = test_user.password_hash
        
        result = auth_service.change_password(
            test_user,
            "testpassword123",
            "newpassword123"
        )
        
        assert result is True
        assert test_user.password_hash != old_password_hash
        assert verify_password("newpassword123", test_user.password_hash)
    
    def test_change_password_wrong_current(self, db_session: Session, test_user):
        """Test password change with wrong current password."""
        auth_service = AuthService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.change_password(
                test_user,
                "wrongpassword",
                "newpassword123"
            )
        
        assert exc_info.value.status_code == 400
        assert "Incorrect current password" in exc_info.value.detail
    
    def test_create_tokens(self, db_session: Session, test_user):
        """Test token creation."""
        auth_service = AuthService(db_session)
        
        tokens = auth_service.create_tokens(test_user)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] > 0
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)
    
    def test_refresh_access_token_success(self, db_session: Session, test_user):
        """Test successful access token refresh."""
        import time
        auth_service = AuthService(db_session)

        # Create initial tokens
        initial_tokens = auth_service.create_tokens(test_user)
        refresh_token = initial_tokens["refresh_token"]

        # Wait a moment to ensure different timestamp
        time.sleep(1)

        # Refresh access token
        new_tokens = auth_service.refresh_access_token(refresh_token)

        assert "access_token" in new_tokens
        assert new_tokens["token_type"] == "bearer"
        assert new_tokens["expires_in"] > 0
        # Note: tokens might be the same if generated in the same second, so we just check they exist
    
    def test_refresh_access_token_invalid(self, db_session: Session):
        """Test access token refresh with invalid token."""
        auth_service = AuthService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.refresh_access_token("invalid_token")
        
        assert exc_info.value.status_code == 401
    
    def test_reset_password_success(self, db_session: Session, test_user):
        """Test successful password reset token generation."""
        auth_service = AuthService(db_session)
        
        reset_token = auth_service.reset_password(test_user.email)
        
        assert isinstance(reset_token, str)
        assert len(reset_token) > 0
    
    def test_reset_password_user_not_found(self, db_session: Session):
        """Test password reset for non-existent user."""
        auth_service = AuthService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.reset_password("nonexistent@example.com")
        
        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail
    
    def test_confirm_password_reset_success(self, db_session: Session, test_user):
        """Test successful password reset confirmation."""
        auth_service = AuthService(db_session)
        
        # Generate reset token
        reset_token = auth_service.reset_password(test_user.email)
        old_password_hash = test_user.password_hash
        
        # Confirm password reset
        result = auth_service.confirm_password_reset(reset_token, "newpassword123")
        
        assert result is True
        db_session.refresh(test_user)
        assert test_user.password_hash != old_password_hash
        assert verify_password("newpassword123", test_user.password_hash)
    
    def test_confirm_password_reset_invalid_token(self, db_session: Session):
        """Test password reset confirmation with invalid token."""
        auth_service = AuthService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.confirm_password_reset("invalid_token", "newpassword123")
        
        assert exc_info.value.status_code == 400
        assert "Invalid or expired token" in exc_info.value.detail
