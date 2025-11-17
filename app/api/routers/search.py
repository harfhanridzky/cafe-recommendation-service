"""
Search API router.
Endpoint for searching cafes near a location.
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Annotated
import logging

from app.schemas.responses import SearchResponse, CafeResponse, ErrorResponse
from app.services.search_service import SearchService
from app.infrastructure.google_places_client import GooglePlacesClient, GooglePlacesAPIError
from app.config import get_settings
from app.domain.models import Cafe

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


def get_search_service() -> SearchService:
    """Dependency to create SearchService instance."""
    settings = get_settings()
    google_client = GooglePlacesClient(api_key=settings.GOOGLE_API_KEY)
    return SearchService(google_places_client=google_client)


def map_cafe_to_response(cafe: Cafe) -> CafeResponse:
    """Map Cafe domain entity to CafeResponse schema."""
    return CafeResponse(
        id=cafe.id,
        name=cafe.name,
        address=cafe.address,
        latitude=cafe.location.latitude,
        longitude=cafe.location.longitude,
        rating=cafe.rating.value,
        price_range=cafe.price_range,
        distance_meters=cafe.distance_meters
    )


@router.get(
    "",
    response_model=SearchResponse,
    summary="Search for cafes near a location",
    description="Search for cafes within a specified radius of a given latitude and longitude",
    responses={
        200: {"description": "Successful search", "model": SearchResponse},
        400: {"description": "Invalid request parameters", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def search_cafes(
    lat: Annotated[float, Query(description="Latitude of search center", ge=-90, le=90)],
    lng: Annotated[float, Query(description="Longitude of search center", ge=-180, le=180)],
    radius: Annotated[int, Query(description="Search radius in meters", ge=1, le=50000)] = 1000,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search for cafes near the specified location.
    
    - **lat**: Latitude (-90 to 90)
    - **lng**: Longitude (-180 to 180)
    - **radius**: Search radius in meters (1 to 50000, default: 1000)
    
    Returns a list of cafes with their details and distance from the search center.
    """
    try:
        logger.info(f"Search request: lat={lat}, lng={lng}, radius={radius}")
        
        # Call search service
        cafes = await search_service.search_cafes(
            latitude=lat,
            longitude=lng,
            radius=radius
        )
        
        # Map to response schema
        cafe_responses = [map_cafe_to_response(cafe) for cafe in cafes]
        
        return SearchResponse(
            total=len(cafe_responses),
            cafes=cafe_responses
        )
        
    except GooglePlacesAPIError as e:
        logger.error(f"Google Places API error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch cafes from Google Places API: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )
