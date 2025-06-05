"""
Database configuration and session management.
"""
import os
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings


# Database engine configuration
def get_database_url() -> str:
    """Get database URL based on environment."""
    if os.getenv("TESTING"):
        return settings.database_test_url or settings.database_url

    # 开发环境使用SQLite
    if settings.environment == "development":
        db_path = os.path.join(os.getcwd(), "data", "geolens.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f"sqlite:///{db_path}"

    return settings.database_url


def get_async_database_url() -> str:
    """Get async database URL for SQLAlchemy async operations."""
    url = get_database_url()
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://")
    return url


# Create database engines
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
)

# Create async engine
async_engine = create_async_engine(
    get_async_database_url(),
    echo=settings.debug,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in get_async_database_url() else {}
)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

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


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database dependency for FastAPI.

    Yields:
        AsyncSession: Async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


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
    """Initialize database tables (sync version)."""
    # Import all models here to ensure they are registered
    from app.models import user, project, mention  # noqa
    from app.models.mention import (
        MentionCheck, MentionResult, BrandMention,
        PromptTemplate, AnalyticsCache
    )  # noqa

    print("🔧 Initializing database tables...")
    print(f"Database URL: {engine.url}")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ Created tables: {tables}")

    # Verify mention-related tables
    required_tables = ['mention_checks', 'mention_results', 'brand_mentions', 'prompt_templates']
    missing_tables = [table for table in required_tables if table not in tables]

    if missing_tables:
        print(f"⚠️ Missing tables: {missing_tables}")
    else:
        print("✅ All required tables created successfully")


async def async_init_db() -> None:
    """Initialize database tables (async version)."""
    # Import all models here to ensure they are registered
    from app.models import user, project  # noqa

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def drop_db() -> None:
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
