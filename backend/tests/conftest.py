"""
Test configuration and fixtures.
"""
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set testing environment
os.environ["TESTING"] = "1"

from app.main import app
from app.core.database import get_db, Base
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.services.auth import AuthService
from app.schemas.user import UserCreate
from app.schemas.project import ProjectCreate


# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_service(db_session):
    """Create authentication service instance."""
    return AuthService(db_session)


@pytest.fixture
def test_user_data():
    """Test user data."""
    return UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
        is_active=True
    )


@pytest.fixture
def test_user(db_session, auth_service, test_user_data):
    """Create test user."""
    user = auth_service.create_user(test_user_data)
    return user


@pytest.fixture
def test_superuser_data():
    """Test superuser data."""
    return UserCreate(
        email="admin@example.com",
        password="adminpassword123",
        full_name="Admin User",
        is_active=True
    )


@pytest.fixture
def test_superuser(db_session, auth_service, test_superuser_data):
    """Create test superuser."""
    user = auth_service.create_user(test_superuser_data)
    user.is_superuser = True
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_project_data():
    """Test project data."""
    return ProjectCreate(
        name="Test Project",
        domain="example.com",
        description="A test project",
        industry="technology",
        target_keywords=["test", "example", "demo"]
    )


@pytest.fixture
def test_project(db_session, test_user, test_project_data):
    """Create test project."""
    from app.services.project import ProjectService
    
    project_service = ProjectService(db_session)
    project = project_service.create_project(test_project_data, str(test_user.id))
    return project


@pytest.fixture
def authenticated_client(client, test_user, auth_service):
    """Create authenticated test client."""
    tokens = auth_service.create_tokens(test_user)
    client.headers.update({
        "Authorization": f"Bearer {tokens['access_token']}"
    })
    return client


@pytest.fixture
def superuser_client(client, test_superuser, auth_service):
    """Create superuser authenticated test client."""
    tokens = auth_service.create_tokens(test_superuser)
    client.headers.update({
        "Authorization": f"Bearer {tokens['access_token']}"
    })
    return client


@pytest.fixture
def mock_current_user(test_user):
    """Mock current user dependency."""
    def override_get_current_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield test_user
    app.dependency_overrides.clear()


# Test data factories
class UserFactory:
    """Factory for creating test users."""
    
    @staticmethod
    def create_user_data(
        email: str = "user@example.com",
        password: str = "password123",
        full_name: str = "Test User"
    ) -> UserCreate:
        return UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            is_active=True
        )


class ProjectFactory:
    """Factory for creating test projects."""
    
    @staticmethod
    def create_project_data(
        name: str = "Test Project",
        domain: str = "example.com",
        description: str = "Test description",
        industry: str = "technology",
        target_keywords: list = None
    ) -> ProjectCreate:
        if target_keywords is None:
            target_keywords = ["test", "example"]
        return ProjectCreate(
            name=name,
            domain=domain,
            description=description,
            industry=industry,
            target_keywords=target_keywords
        )
