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
    database_url: str = Field(default="sqlite:///./data/geolens.db", env="DATABASE_URL")
    database_test_url: Optional[str] = Field(default="sqlite:///./data/test.db", env="DATABASE_TEST_URL")
    
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
    doubao_default_model: str = Field(default="doubao-1-5-lite-32k-250115", env="DOUBAO_DEFAULT_MODEL")

    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", env="DEEPSEEK_BASE_URL")
    deepseek_default_model: str = Field(default="deepseek-reasoner", env="DEEPSEEK_DEFAULT_MODEL")

    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    openai_default_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_DEFAULT_MODEL")

    claude_api_key: Optional[str] = Field(default=None, env="CLAUDE_API_KEY")
    claude_base_url: str = Field(default="https://api.anthropic.com", env="CLAUDE_BASE_URL")
    claude_default_model: str = Field(default="claude-3-sonnet-20240229", env="CLAUDE_DEFAULT_MODEL")

    # AI Service General Settings
    ai_request_timeout: int = Field(default=30, env="AI_REQUEST_TIMEOUT")
    ai_max_retries: int = Field(default=3, env="AI_MAX_RETRIES")
    ai_retry_delay: float = Field(default=1.0, env="AI_RETRY_DELAY")
    default_ai_provider: str = Field(default="doubao", env="DEFAULT_AI_PROVIDER")

    # Mention Detection Settings
    default_detection_strategy: str = Field(default="improved", env="DEFAULT_DETECTION_STRATEGY")
    max_concurrent_detections: int = Field(default=5, env="MAX_CONCURRENT_DETECTIONS")
    detection_timeout: int = Field(default=60, env="DETECTION_TIMEOUT")
    brand_detection_cache_ttl: int = Field(default=3600, env="BRAND_DETECTION_CACHE_TTL")
    
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

    def get_ai_model_config(self, provider: str) -> dict:
        """Get AI model configuration for a specific provider."""
        configs = {
            "doubao": {
                "api_key": self.doubao_api_key,
                "base_url": self.doubao_base_url,
                "default_model": self.doubao_default_model
            },
            "deepseek": {
                "api_key": self.deepseek_api_key,
                "base_url": self.deepseek_base_url,
                "default_model": self.deepseek_default_model
            },
            "openai": {
                "api_key": self.openai_api_key,
                "base_url": self.openai_base_url,
                "default_model": self.openai_default_model
            },
            "claude": {
                "api_key": self.claude_api_key,
                "base_url": self.claude_base_url,
                "default_model": self.claude_default_model
            }
        }

        if provider not in configs:
            raise ValueError(f"Unsupported AI provider: {provider}")

        return configs[provider]

    def get_database_url(self, for_testing: bool = False) -> str:
        """Get database URL for the specified environment."""
        if for_testing and self.database_test_url:
            return self.database_test_url
        return self.database_url

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def get_available_ai_providers(self) -> List[str]:
        """Get list of available AI providers with API keys."""
        providers = []
        if self.doubao_api_key:
            providers.append("doubao")
        if self.deepseek_api_key:
            providers.append("deepseek")
        if self.openai_api_key:
            providers.append("openai")
        if self.claude_api_key:
            providers.append("claude")
        return providers


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
