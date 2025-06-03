"""
Unit tests for project service.
"""
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.project import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.common import PaginationParams
from tests.conftest import ProjectFactory


class TestProjectService:
    """Test project service."""
    
    def test_create_project_success(self, db_session: Session, test_user):
        """Test successful project creation."""
        project_service = ProjectService(db_session)
        project_data = ProjectFactory.create_project_data(
            name="New Project",
            domain="newproject.com"
        )
        
        project = project_service.create_project(project_data, str(test_user.id))
        
        assert project.name == project_data.name
        assert project.domain == project_data.domain.lower()
        assert project.description == project_data.description
        assert project.industry == project_data.industry
        assert project.target_keywords == project_data.target_keywords
        assert project.user_id == test_user.id
        assert project.is_active is True
        assert project.id is not None
        assert project.created_at is not None
    
    def test_create_project_duplicate_domain(self, db_session: Session, test_user, test_project):
        """Test project creation with duplicate domain for same user."""
        project_service = ProjectService(db_session)
        project_data = ProjectFactory.create_project_data(domain=test_project.domain)
        
        with pytest.raises(HTTPException) as exc_info:
            project_service.create_project(project_data, str(test_user.id))
        
        assert exc_info.value.status_code == 400
        assert "Project with this domain already exists" in exc_info.value.detail
    
    def test_create_project_same_domain_different_user(self, db_session: Session, test_user, test_project, auth_service):
        """Test project creation with same domain for different user."""
        # Create another user
        from tests.conftest import UserFactory
        user_data = UserFactory.create_user_data(email="another@example.com")
        another_user = auth_service.create_user(user_data)
        
        project_service = ProjectService(db_session)
        project_data = ProjectFactory.create_project_data(domain=test_project.domain)
        
        # Should succeed for different user
        project = project_service.create_project(project_data, str(another_user.id))
        
        assert project.domain == test_project.domain
        assert project.user_id == another_user.id
        assert project.user_id != test_project.user_id
    
    def test_get_project_by_id_exists(self, db_session: Session, test_user, test_project):
        """Test getting project by ID when project exists."""
        project_service = ProjectService(db_session)
        
        project = project_service.get_project_by_id(str(test_project.id), str(test_user.id))
        
        assert project is not None
        assert project.id == test_project.id
        assert project.user_id == test_user.id
    
    def test_get_project_by_id_not_exists(self, db_session: Session, test_user):
        """Test getting project by ID when project doesn't exist."""
        project_service = ProjectService(db_session)
        
        project = project_service.get_project_by_id(
            "00000000-0000-0000-0000-000000000000",
            str(test_user.id)
        )
        
        assert project is None
    
    def test_get_project_by_id_wrong_user(self, db_session: Session, test_project, auth_service):
        """Test getting project by ID with wrong user."""
        # Create another user
        from tests.conftest import UserFactory
        user_data = UserFactory.create_user_data(email="another@example.com")
        another_user = auth_service.create_user(user_data)
        
        project_service = ProjectService(db_session)
        
        project = project_service.get_project_by_id(
            str(test_project.id),
            str(another_user.id)
        )
        
        assert project is None
    
    def test_get_project_by_domain_exists(self, db_session: Session, test_user, test_project):
        """Test getting project by domain when project exists."""
        project_service = ProjectService(db_session)
        
        project = project_service.get_project_by_domain(test_project.domain, str(test_user.id))
        
        assert project is not None
        assert project.id == test_project.id
        assert project.domain == test_project.domain
    
    def test_get_project_by_domain_not_exists(self, db_session: Session, test_user):
        """Test getting project by domain when project doesn't exist."""
        project_service = ProjectService(db_session)
        
        project = project_service.get_project_by_domain("nonexistent.com", str(test_user.id))
        
        assert project is None
    
    def test_update_project_success(self, db_session: Session, test_project):
        """Test successful project update."""
        project_service = ProjectService(db_session)
        update_data = ProjectUpdate(
            name="Updated Project",
            description="Updated description",
            target_keywords=["updated", "keywords"]
        )
        
        updated_project = project_service.update_project(test_project, update_data)
        
        assert updated_project.name == "Updated Project"
        assert updated_project.description == "Updated description"
        assert updated_project.target_keywords == ["updated", "keywords"]
        assert updated_project.domain == test_project.domain  # Unchanged
    
    def test_delete_project_success(self, db_session: Session, test_project):
        """Test successful project deletion."""
        project_service = ProjectService(db_session)
        project_id = test_project.id
        
        result = project_service.delete_project(test_project)
        
        assert result is True
        
        # Verify project is deleted
        from app.models.project import Project
        deleted_project = db_session.query(Project).filter_by(id=project_id).first()
        assert deleted_project is None
    
    def test_get_user_projects_pagination(self, db_session: Session, test_user, auth_service):
        """Test getting user projects with pagination."""
        project_service = ProjectService(db_session)
        
        # Create multiple projects
        for i in range(5):
            project_data = ProjectFactory.create_project_data(
                name=f"Project {i}",
                domain=f"project{i}.com"
            )
            project_service.create_project(project_data, str(test_user.id))
        
        # Test pagination
        pagination = PaginationParams(page=1, per_page=3)
        projects, total = project_service.get_user_projects(str(test_user.id), pagination)
        
        assert len(projects) == 3
        assert total == 5
        
        # Test second page
        pagination = PaginationParams(page=2, per_page=3)
        projects, total = project_service.get_user_projects(str(test_user.id), pagination)
        
        assert len(projects) == 2
        assert total == 5
    
    def test_get_user_projects_filter_active(self, db_session: Session, test_user, auth_service):
        """Test getting user projects filtered by active status."""
        project_service = ProjectService(db_session)
        
        # Create active and inactive projects
        active_data = ProjectFactory.create_project_data(name="Active", domain="active.com")
        active_project = project_service.create_project(active_data, str(test_user.id))
        
        inactive_data = ProjectFactory.create_project_data(name="Inactive", domain="inactive.com")
        inactive_project = project_service.create_project(inactive_data, str(test_user.id))
        inactive_project.is_active = False
        db_session.commit()
        
        pagination = PaginationParams(page=1, per_page=10)
        
        # Test active filter
        projects, total = project_service.get_user_projects(
            str(test_user.id), pagination, is_active=True
        )
        assert total == 1
        assert projects[0].is_active is True
        
        # Test inactive filter
        projects, total = project_service.get_user_projects(
            str(test_user.id), pagination, is_active=False
        )
        assert total == 1
        assert projects[0].is_active is False
    
    def test_get_user_projects_search(self, db_session: Session, test_user, auth_service):
        """Test getting user projects with search."""
        project_service = ProjectService(db_session)
        
        # Create projects with different names and domains
        project_data1 = ProjectFactory.create_project_data(name="Search Test", domain="search.com")
        project_service.create_project(project_data1, str(test_user.id))
        
        project_data2 = ProjectFactory.create_project_data(name="Another Project", domain="another.com")
        project_service.create_project(project_data2, str(test_user.id))
        
        pagination = PaginationParams(page=1, per_page=10)
        
        # Search by name
        projects, total = project_service.get_user_projects(
            str(test_user.id), pagination, search="Search"
        )
        assert total == 1
        assert "Search" in projects[0].name
        
        # Search by domain
        projects, total = project_service.get_user_projects(
            str(test_user.id), pagination, search="another"
        )
        assert total == 1
        assert "another" in projects[0].domain
    
    def test_get_project_stats(self, db_session: Session, test_user, auth_service):
        """Test getting project statistics."""
        project_service = ProjectService(db_session)
        
        # Create projects with different statuses and keywords
        active_data = ProjectFactory.create_project_data(
            name="Active",
            domain="active.com",
            target_keywords=["keyword1", "keyword2"]
        )
        active_project = project_service.create_project(active_data, str(test_user.id))
        
        inactive_data = ProjectFactory.create_project_data(
            name="Inactive",
            domain="inactive.com",
            target_keywords=["keyword3"]
        )
        inactive_project = project_service.create_project(inactive_data, str(test_user.id))
        inactive_project.is_active = False
        db_session.commit()
        
        stats = project_service.get_project_stats(str(test_user.id))
        
        assert stats["total_projects"] == 2
        assert stats["active_projects"] == 1
        assert stats["inactive_projects"] == 1
        assert stats["total_keywords"] == 3
        assert stats["avg_keywords_per_project"] == 1.5
    
    def test_toggle_project_status(self, db_session: Session, test_project):
        """Test toggling project status."""
        project_service = ProjectService(db_session)
        original_status = test_project.is_active
        
        updated_project = project_service.toggle_project_status(test_project)
        
        assert updated_project.is_active != original_status
        
        # Toggle again
        updated_project = project_service.toggle_project_status(test_project)
        assert updated_project.is_active == original_status
    
    def test_add_keywords_success(self, db_session: Session, test_project):
        """Test successfully adding keywords."""
        project_service = ProjectService(db_session)
        new_keywords = ["new1", "new2"]
        original_keywords = test_project.target_keywords.copy()
        
        updated_project = project_service.add_keywords(test_project, new_keywords)
        
        expected_keywords = list(set(original_keywords + new_keywords))
        assert set(updated_project.target_keywords) == set(expected_keywords)
    
    def test_add_keywords_max_limit(self, db_session: Session, test_project):
        """Test adding keywords exceeding maximum limit."""
        project_service = ProjectService(db_session)
        
        # Set project to have 19 keywords (close to limit of 20)
        test_project.target_keywords = [f"keyword{i}" for i in range(19)]
        db_session.commit()
        
        # Try to add 2 more keywords (would exceed limit)
        with pytest.raises(HTTPException) as exc_info:
            project_service.add_keywords(test_project, ["new1", "new2"])
        
        assert exc_info.value.status_code == 400
        assert "Maximum 20 keywords allowed" in exc_info.value.detail
    
    def test_remove_keywords_success(self, db_session: Session, test_project):
        """Test successfully removing keywords."""
        project_service = ProjectService(db_session)
        original_keywords = test_project.target_keywords.copy() if test_project.target_keywords else []

        if not original_keywords:
            # If no keywords, add some first
            test_project.target_keywords = ["test", "example", "demo"]
            db_session.commit()
            original_keywords = test_project.target_keywords.copy()

        keywords_to_remove = [original_keywords[0]]

        updated_project = project_service.remove_keywords(test_project, keywords_to_remove)

        assert keywords_to_remove[0] not in updated_project.target_keywords
        assert len(updated_project.target_keywords) == len(original_keywords) - 1
