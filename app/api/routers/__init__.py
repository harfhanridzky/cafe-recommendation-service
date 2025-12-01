"""
API Routers package.
Contains all FastAPI routers for the application.
"""
from app.api.routers import auth, search, recommendations

__all__ = ["auth", "search", "recommendations"]
