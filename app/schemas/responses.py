"""
Pydantic schemas for API responses.
Maps domain models to API response formats.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

from app.domain.models import PriceRange


class LocationResponse(BaseModel):
    """Response schema for location data."""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")


class CafeResponse(BaseModel):
    """Response schema for a single cafe."""
    id: str = Field(..., description="Unique cafe identifier (Google place_id)")
    name: str = Field(..., description="Cafe name")
    address: str = Field(..., description="Cafe address")
    latitude: float = Field(..., description="Cafe latitude")
    longitude: float = Field(..., description="Cafe longitude")
    rating: float = Field(..., ge=0.0, le=5.0, description="Rating (0.0 - 5.0)")
    price_range: PriceRange = Field(..., description="Price range category")
    distance_meters: Optional[float] = Field(None, description="Distance from search location in meters")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                "name": "Cafe Latte",
                "address": "123 Main Street, Bandung",
                "latitude": -6.9175,
                "longitude": 107.6191,
                "rating": 4.5,
                "price_range": "MEDIUM",
                "distance_meters": 250.5
            }
        }


class SearchResponse(BaseModel):
    """Response schema for search endpoint."""
    total: int = Field(..., description="Total number of cafes found")
    cafes: List[CafeResponse] = Field(..., description="List of cafes")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "total": 2,
                "cafes": [
                    {
                        "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                        "name": "Cafe Latte",
                        "address": "123 Main Street, Bandung",
                        "latitude": -6.9175,
                        "longitude": 107.6191,
                        "rating": 4.5,
                        "price_range": "MEDIUM",
                        "distance_meters": 250.5
                    }
                ]
            }
        }


class RecommendationResponse(BaseModel):
    """Response schema for recommendations endpoint."""
    total: int = Field(..., description="Total number of recommended cafes")
    cafes: List[CafeResponse] = Field(..., description="List of recommended cafes (sorted by rating then distance)")
    filters_applied: dict = Field(..., description="Filters that were applied")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "total": 1,
                "cafes": [
                    {
                        "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                        "name": "Cafe Latte",
                        "address": "123 Main Street, Bandung",
                        "latitude": -6.9175,
                        "longitude": 107.6191,
                        "rating": 4.5,
                        "price_range": "MEDIUM",
                        "distance_meters": 250.5
                    }
                ],
                "filters_applied": {
                    "min_rating": 4.2,
                    "price_ranges": ["MEDIUM", "HIGH"],
                    "limit": 20
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "Invalid coordinates",
                "detail": "Latitude must be between -90 and 90"
            }
        }
