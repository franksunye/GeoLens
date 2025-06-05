"""
Integration tests for authentication API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from tests.conftest import UserFactory


class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        user_data = UserFactory.create_user_data(email="newuser@example.com")
        
        response = client.post("/api/v1/auth/register", json=user_data.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User registered successfully"
        assert data["data"]["email"] == user_data.email
        assert data["data"]["full_name"] == user_data.full_name
        assert data["data"]["is_active"] is True
        assert "id" in data["data"]
        assert "password" not in data["data"]
    
    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email."""
        user_data = UserFactory.create_user_data(email=test_user.email)
        
        response = client.post("/api/v1/auth/register", json=user_data.dict())
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Email already registered" in data["error"]["message"]
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User",
            "is_active": True
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422
    
    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password."""
        user_data = {
            "email": "user@example.com",
            "password": "weak",
            "full_name": "Test User",
            "is_active": True
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422
    
    def test_login_success(self, client: TestClient, test_user):
        """Test successful login."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Login successful"
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["expires_in"] > 0
        assert data["data"]["user"]["email"] == test_user.email
    
    def test_login_wrong_email(self, client: TestClient):
        """Test login with wrong email."""
        login_data = {
            "email": "wrong@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Incorrect email or password" in data["error"]["message"]
    
    def test_login_wrong_password(self, client: TestClient, test_user):
        """Test login with wrong password."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Incorrect email or password" in data["error"]["message"]
    
    def test_login_inactive_user(self, client: TestClient, test_user, db_session):
        """Test login with inactive user."""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()
        
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Inactive user" in data["error"]["message"]
    
    def test_refresh_token_success(self, client: TestClient, test_user, auth_service):
        """Test successful token refresh."""
        # Get initial tokens
        tokens = auth_service.create_tokens(test_user)
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Token refreshed successfully"
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["expires_in"] > 0
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test token refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
    
    def test_get_current_user_success(self, authenticated_client: TestClient, test_user):
        """Test getting current user profile."""
        response = authenticated_client.get("/api/v1/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User profile retrieved successfully"
        assert data["data"]["email"] == test_user.email
        assert data["data"]["full_name"] == test_user.full_name
        assert "is_premium" in data["data"]
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 403
    
    def test_update_current_user_success(self, authenticated_client: TestClient, test_user):
        """Test updating current user profile."""
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
        
        response = authenticated_client.put("/api/v1/auth/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User profile updated successfully"
        assert data["data"]["full_name"] == "Updated Name"
        assert data["data"]["bio"] == "Updated bio"
    
    def test_change_password_success(self, authenticated_client: TestClient, test_user):
        """Test successful password change."""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        
        response = authenticated_client.post("/api/v1/auth/change-password", json=password_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Password changed successfully"
        assert data["data"]["success"] is True
    
    def test_change_password_wrong_current(self, authenticated_client: TestClient):
        """Test password change with wrong current password."""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        response = authenticated_client.post("/api/v1/auth/change-password", json=password_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Incorrect current password" in data["error"]["message"]
    
    def test_reset_password_success(self, client: TestClient, test_user):
        """Test successful password reset request."""
        reset_data = {"email": test_user.email}
        
        response = client.post("/api/v1/auth/reset-password", json=reset_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Password reset token generated"
        assert "reset_token" in data["data"]
    
    def test_reset_password_user_not_found(self, client: TestClient):
        """Test password reset for non-existent user."""
        reset_data = {"email": "nonexistent@example.com"}
        
        response = client.post("/api/v1/auth/reset-password", json=reset_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "User not found" in data["error"]["message"]
    
    def test_confirm_password_reset_success(self, client: TestClient, test_user, auth_service):
        """Test successful password reset confirmation."""
        # Generate reset token
        reset_token = auth_service.reset_password(test_user.email)
        
        reset_data = {
            "token": reset_token,
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/reset-password/confirm", json=reset_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Password reset successfully"
        assert data["data"]["success"] is True
    
    def test_confirm_password_reset_invalid_token(self, client: TestClient):
        """Test password reset confirmation with invalid token."""
        reset_data = {
            "token": "invalid_token",
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/reset-password/confirm", json=reset_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Invalid or expired token" in data["error"]["message"]
