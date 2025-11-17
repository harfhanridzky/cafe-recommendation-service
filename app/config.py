"""
Configuration module for the Cafe Recommendation Service.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    GOOGLE_API_KEY: str
    APP_NAME: str = "Cafe Recommendation Service"
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
