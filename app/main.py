"""
Main FastAPI application for Cafe Recommendation Service.
Coordinates all bounded contexts:
- BC1 (Catalog): Domain models and mapping
- BC2 (Search): Search orchestration
- BC3 (Recommendation): Filtering and ranking

Plus JWT-based authentication for protected endpoints.
"""
from dotenv import load_dotenv
import os

# Load .env file at startup
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.api.routers import search, recommendations, auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    Cafe Recommendation Service API
    
    This service helps you discover and get recommendations for cafes near your location.
    
    ## Features
    
    * **Authentication**: JWT-based authentication for secure access
    * **Search**: Find cafes within a specified radius (public)
    * **Recommend**: Get filtered and ranked cafe recommendations (protected)
    
    ## Authentication
    
    1. Register a new account at `/api/v1/auth/register`
    2. Login at `/api/v1/auth/login` to get a JWT token
    3. Use the token in the Authorization header: `Bearer <token>`
    
    ## Bounded Contexts
    
    * **BC1 (Catalog)**: Maps Google Places data to domain entities
    * **BC2 (Search)**: Orchestrates cafe search operations
    * **BC3 (Recommendation)**: Applies filters and ranking logic
    
    All data comes from Google Places API in real-time.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(search.router, prefix=settings.API_V1_PREFIX)
app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "Cafe Recommendation Service API",
        "endpoints": {
            "docs": "/docs",
            "auth": f"{settings.API_V1_PREFIX}/auth",
            "search": f"{settings.API_V1_PREFIX}/search",
            "recommendations": f"{settings.API_V1_PREFIX}/recommendations"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


@app.on_event("startup")
async def startup_event():
    """Log startup message."""
    logger.info(f"{settings.APP_NAME} started successfully")
    logger.info(f"API documentation available at: /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown message."""
    logger.info(f"{settings.APP_NAME} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
