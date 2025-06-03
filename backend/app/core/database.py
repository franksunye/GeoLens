"""
Database configuration and session management.
"""
import os
from typing import Generator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings


# Database engine configuration
def get_database_url() -> str:
    """Get database URL based on environment."""
    if os.getenv("TESTING"):
        return settings.database_test_url or settings.database_url
    return settings.database_url


# Create database engine
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_test_engine():
    """Create test database engine."""
    test_url = settings.database_test_url or "sqlite:///./test.db"
    
    if test_url.startswith("sqlite"):
        # SQLite configuration for testing
        return create_engine(
            test_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )
    else:
        # PostgreSQL configuration for testing
        return create_engine(
            test_url,
            pool_pre_ping=True,
            echo=False,
        )


def create_test_session():
    """Create test database session."""
    test_engine = create_test_engine()
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    return TestSessionLocal, test_engine


def init_db() -> None:
    """Initialize database tables."""
    # Import all models here to ensure they are registered
    from app.models import user, project  # noqa
    
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
