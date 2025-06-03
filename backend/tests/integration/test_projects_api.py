"""
Integration tests for projects API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from tests.conftest import ProjectFactory


class TestProjectsAPI:
    """Test projects API endpoints."""
    
    def test_create_project_success(self, authenticated_client: TestClient):
        """Test successful project creation."""
        project_data = ProjectFactory.create_project_data(
            name="New Project",
            domain="newproject.com"
        )
        
        response = authenticated_client.post("/api/v1/projects/", json=project_data.dict())
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Project created successfully"
        assert data["data"]["name"] == project_data.name
        assert data["data"]["domain"] == project_data.domain.lower()
        assert data["data"]["description"] == project_data.description
        assert data["data"]["industry"] == project_data.industry
        assert data["data"]["target_keywords"] == project_data.target_keywords
        assert data["data"]["is_active"] is True
        assert "id" in data["data"]
        assert "user_id" in data["data"]
    
    def test_create_project_unauthorized(self, client: TestClient):
        """Test project creation without authentication."""
        project_data = ProjectFactory.create_project_data()
        
        response = client.post("/api/v1/projects/", json=project_data.dict())
        
        assert response.status_code == 401
    
    def test_create_project_duplicate_domain(self, authenticated_client: TestClient, test_project):
        """Test project creation with duplicate domain."""
        project_data = ProjectFactory.create_project_data(domain=test_project.domain)
        
        response = authenticated_client.post("/api/v1/projects/", json=project_data.dict())
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Project with this domain already exists" in data["error"]["message"]
    
    def test_create_project_invalid_domain(self, authenticated_client: TestClient):
        """Test project creation with invalid domain."""
        project_data = ProjectFactory.create_project_data(domain="invalid-domain")
        
        response = authenticated_client.post("/api/v1/projects/", json=project_data.dict())
        
        assert response.status_code == 422
    
    def test_get_projects_success(self, authenticated_client: TestClient, test_project):
        """Test getting user projects."""
        response = authenticated_client.get("/api/v1/projects/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Projects retrieved successfully"
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "per_page" in data["data"]
        assert data["data"]["total"] >= 1
        
        # Check if test project is in the list
        project_ids = [p["id"] for p in data["data"]["items"]]
        assert str(test_project.id) in project_ids
    
    def test_get_projects_pagination(self, authenticated_client: TestClient, test_user, db_session):
        """Test projects pagination."""
        # Create multiple projects
        from app.services.project import ProjectService
        project_service = ProjectService(db_session)
        
        for i in range(5):
            project_data = ProjectFactory.create_project_data(
                name=f"Project {i}",
                domain=f"project{i}.com"
            )
            project_service.create_project(project_data, str(test_user.id))
        
        # Test first page
        response = authenticated_client.get("/api/v1/projects/?page=1&per_page=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 3
        assert data["data"]["total"] == 5
        assert data["data"]["page"] == 1
        assert data["data"]["has_next"] is True
        assert data["data"]["has_prev"] is False
        
        # Test second page
        response = authenticated_client.get("/api/v1/projects/?page=2&per_page=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["items"]) == 2
        assert data["data"]["page"] == 2
        assert data["data"]["has_next"] is False
        assert data["data"]["has_prev"] is True
    
    def test_get_projects_filter_active(self, authenticated_client: TestClient, test_user, db_session):
        """Test projects filtering by active status."""
        from app.services.project import ProjectService
        project_service = ProjectService(db_session)
        
        # Create active project
        active_data = ProjectFactory.create_project_data(name="Active", domain="active.com")
        active_project = project_service.create_project(active_data, str(test_user.id))
        
        # Create inactive project
        inactive_data = ProjectFactory.create_project_data(name="Inactive", domain="inactive.com")
        inactive_project = project_service.create_project(inactive_data, str(test_user.id))
        inactive_project.is_active = False
        db_session.commit()
        
        # Test active filter
        response = authenticated_client.get("/api/v1/projects/?is_active=true")
        
        assert response.status_code == 200
        data = response.json()
        assert all(p["is_active"] for p in data["data"]["items"])
        
        # Test inactive filter
        response = authenticated_client.get("/api/v1/projects/?is_active=false")
        
        assert response.status_code == 200
        data = response.json()
        assert all(not p["is_active"] for p in data["data"]["items"])
    
    def test_get_projects_search(self, authenticated_client: TestClient, test_user, db_session):
        """Test projects search functionality."""
        from app.services.project import ProjectService
        project_service = ProjectService(db_session)
        
        # Create projects with different names
        search_data = ProjectFactory.create_project_data(name="Search Test", domain="search.com")
        project_service.create_project(search_data, str(test_user.id))
        
        another_data = ProjectFactory.create_project_data(name="Another Project", domain="another.com")
        project_service.create_project(another_data, str(test_user.id))
        
        # Search by name
        response = authenticated_client.get("/api/v1/projects/?search=Search")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] >= 1
        assert any("Search" in p["name"] for p in data["data"]["items"])
    
    def test_get_project_stats(self, authenticated_client: TestClient, test_project):
        """Test getting project statistics."""
        response = authenticated_client.get("/api/v1/projects/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Project statistics retrieved successfully"
        assert "total_projects" in data["data"]
        assert "active_projects" in data["data"]
        assert "inactive_projects" in data["data"]
        assert "total_keywords" in data["data"]
        assert "avg_keywords_per_project" in data["data"]
        assert data["data"]["total_projects"] >= 1
    
    def test_get_project_by_id_success(self, authenticated_client: TestClient, test_project):
        """Test getting project by ID."""
        response = authenticated_client.get(f"/api/v1/projects/{test_project.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Project retrieved successfully"
        assert data["data"]["id"] == str(test_project.id)
        assert data["data"]["name"] == test_project.name
        assert data["data"]["domain"] == test_project.domain
        assert "owner" in data["data"]
    
    def test_get_project_by_id_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent project."""
        response = authenticated_client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "Project not found" in data["error"]["message"]
    
    def test_update_project_success(self, authenticated_client: TestClient, test_project):
        """Test successful project update."""
        update_data = {
            "name": "Updated Project",
            "description": "Updated description",
            "target_keywords": ["updated", "keywords"]
        }
        
        response = authenticated_client.put(f"/api/v1/projects/{test_project.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Project updated successfully"
        assert data["data"]["name"] == "Updated Project"
        assert data["data"]["description"] == "Updated description"
        assert data["data"]["target_keywords"] == ["updated", "keywords"]
    
    def test_update_project_not_found(self, authenticated_client: TestClient):
        """Test updating non-existent project."""
        update_data = {"name": "Updated Project"}
        
        response = authenticated_client.put(
            "/api/v1/projects/00000000-0000-0000-0000-000000000000",
            json=update_data
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "Project not found" in data["error"]["message"]
    
    def test_delete_project_success(self, authenticated_client: TestClient, test_project):
        """Test successful project deletion."""
        response = authenticated_client.delete(f"/api/v1/projects/{test_project.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Project deleted successfully"
        assert data["data"]["success"] is True
        
        # Verify project is deleted
        get_response = authenticated_client.get(f"/api/v1/projects/{test_project.id}")
        assert get_response.status_code == 404
    
    def test_delete_project_not_found(self, authenticated_client: TestClient):
        """Test deleting non-existent project."""
        response = authenticated_client.delete("/api/v1/projects/00000000-0000-0000-0000-000000000000")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "Project not found" in data["error"]["message"]
    
    def test_toggle_project_status(self, authenticated_client: TestClient, test_project):
        """Test toggling project status."""
        original_status = test_project.is_active
        
        response = authenticated_client.post(f"/api/v1/projects/{test_project.id}/toggle")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_active"] != original_status
        
        # Toggle back
        response = authenticated_client.post(f"/api/v1/projects/{test_project.id}/toggle")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["is_active"] == original_status
    
    def test_add_keywords_success(self, authenticated_client: TestClient, test_project):
        """Test successfully adding keywords."""
        keywords = ["new1", "new2"]
        
        response = authenticated_client.post(
            f"/api/v1/projects/{test_project.id}/keywords",
            json=keywords
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Keywords added successfully"
        assert "new1" in data["data"]["target_keywords"]
        assert "new2" in data["data"]["target_keywords"]
    
    def test_remove_keywords_success(self, authenticated_client: TestClient, test_project):
        """Test successfully removing keywords."""
        # Ensure project has keywords to remove
        keywords_to_remove = [test_project.target_keywords[0]] if test_project.target_keywords else ["test"]
        
        response = authenticated_client.request(
            "DELETE",
            f"/api/v1/projects/{test_project.id}/keywords",
            json=keywords_to_remove
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Keywords removed successfully"
        
        if test_project.target_keywords:
            assert keywords_to_remove[0] not in data["data"]["target_keywords"]
