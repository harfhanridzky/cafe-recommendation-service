"""
Configuration module for the Cafe Recommendation Service.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google API Key - read from environment with empty default
    GOOGLE_API_KEY: str = ""
    APP_NAME: str = "Cafe Recommendation Service"
    API_V1_PREFIX: str = "/api/v1"
    
    # JWT Configuration - read from environment with fallback
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production-minimum-32-characters"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from environment

    def __init__(self, **kwargs):
        """Initialize settings with environment variables."""
        # Read from OS environment first (for Vercel)
        env_values = {
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
            "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production-minimum-32-characters"),
            "JWT_ALGORITHM": os.getenv("JWT_ALGORITHM", "HS256"),
            "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        }
        # Merge with provided kwargs
        env_values.update(kwargs)
        super().__init__(**env_values)


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    settings = Settings()
    
    # Validate critical settings
    if not settings.GOOGLE_API_KEY:
        import warnings
        warnings.warn(
            "⚠️  GOOGLE_API_KEY is not set. API calls to Google Places will fail. "
            "Please set GOOGLE_API_KEY environment variable in Vercel dashboard: "
            "Project Settings → Environment Variables"
        )
    
    return settings
