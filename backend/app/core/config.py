"""
Application configuration settings.
"""
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = Field(default="GEO Insight API", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_test_url: Optional[str] = Field(default=None, env="DATABASE_TEST_URL")
    
    # Supabase (Alternative)
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    supabase_service_key: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_KEY")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_test_url: str = Field(default="redis://localhost:6379/1", env="REDIS_TEST_URL")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # AI Services
    doubao_api_key: Optional[str] = Field(default=None, env="DOUBAO_API_KEY")
    doubao_base_url: str = Field(default="https://ark.cn-beijing.volces.com/api/v3", env="DOUBAO_BASE_URL")
    doubao_default_model: str = Field(default="doubao-pro-32k", env="DOUBAO_DEFAULT_MODEL")

    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", env="DEEPSEEK_BASE_URL")
    deepseek_default_model: str = Field(default="deepseek-chat", env="DEEPSEEK_DEFAULT_MODEL")

    # AI Service General Settings
    ai_request_timeout: int = Field(default=30, env="AI_REQUEST_TIMEOUT")
    ai_max_retries: int = Field(default=3, env="AI_MAX_RETRIES")
    ai_retry_delay: float = Field(default=1.0, env="AI_RETRY_DELAY")
    default_ai_provider: str = Field(default="doubao", env="DEFAULT_AI_PROVIDER")
    
    # External Services
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"], 
        env="ALLOWED_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    @validator("allowed_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format."""
        # Allow SQLite for testing
        if v.startswith("sqlite://"):
            return v
        if not v.startswith(("postgresql://", "postgresql+psycopg2://")):
            raise ValueError("Database URL must be a PostgreSQL or SQLite URL")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
