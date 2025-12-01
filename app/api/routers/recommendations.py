"""
Recommendations API router.
Endpoint for getting filtered and ranked cafe recommendations.

This endpoint is protected and requires JWT authentication.
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Annotated, List, Optional
import logging

from app.schemas.responses import RecommendationResponse, CafeResponse, ErrorResponse
from app.services.search_service import SearchService
from app.services.recommendation_service import RecommendationService
from app.infrastructure.google_places_client import GooglePlacesClient, GooglePlacesAPIError
from app.config import get_settings
from app.domain.models import Cafe, PriceRange, User
from app.api.dependencies import CurrentUser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_search_service() -> SearchService:
    """Dependency to create SearchService instance."""
    settings = get_settings()
    google_client = GooglePlacesClient(api_key=settings.GOOGLE_API_KEY)
    return SearchService(google_places_client=google_client)


def get_recommendation_service() -> RecommendationService:
    """Dependency to create RecommendationService instance."""
    return RecommendationService()


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


def parse_price_ranges(price_range_str: Optional[str]) -> Optional[List[PriceRange]]:
    """
    Parse price range query parameter into list of PriceRange enums.
    
    Args:
        price_range_str: Comma-separated price ranges (e.g., "CHEAP,MEDIUM") or None
    
    Returns:
        List of PriceRange enums or None if input is None
    """
    if not price_range_str:
        return None
    
    # Split by comma and strip whitespace
    range_strs = [r.strip().upper() for r in price_range_str.split(",")]
    
    # Convert to PriceRange enums
    try:
        return [PriceRange(r) for r in range_strs if r]
    except ValueError as e:
        valid_ranges = ", ".join([pr.value for pr in PriceRange])
        raise ValueError(f"Invalid price range. Valid values: {valid_ranges}") from e


@router.get(
    "",
    response_model=RecommendationResponse,
    summary="Get cafe recommendations",
    description="Get filtered and ranked cafe recommendations based on rating and price preferences. **Requires JWT authentication.**",
    responses={
        200: {"description": "Successful recommendations", "model": RecommendationResponse},
        400: {"description": "Invalid request parameters", "model": ErrorResponse},
        401: {"description": "Not authenticated - valid JWT token required"},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_recommendations(
    lat: Annotated[float, Query(description="Latitude of search center", ge=-90, le=90)],
    lng: Annotated[float, Query(description="Longitude of search center", ge=-180, le=180)],
    radius: Annotated[int, Query(description="Search radius in meters", ge=1, le=50000)] = 1000,
    min_rating: Annotated[float, Query(description="Minimum rating filter", ge=0, le=5)] = 0.0,
    price_range: Annotated[
        Optional[str], 
        Query(description="Comma-separated price ranges (e.g., 'CHEAP,MEDIUM,HIGH')")
    ] = None,
    limit: Annotated[int, Query(description="Maximum number of results", ge=1, le=100)] = 20,
    current_user: CurrentUser = None,  # JWT Protection - requires authentication
    search_service: SearchService = Depends(get_search_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get cafe recommendations with filters and ranking.
    
    - **lat**: Latitude (-90 to 90)
    - **lng**: Longitude (-180 to 180)
    - **radius**: Search radius in meters (1 to 50000, default: 1000)
    - **min_rating**: Minimum rating (0 to 5, default: 0)
    - **price_range**: Comma-separated price ranges (CHEAP, MEDIUM, HIGH, VERY_HIGH, LUXURY, UNKNOWN)
    - **limit**: Maximum results (1 to 100, default: 20)
    
    **Authentication**: Requires valid JWT token in Authorization header.
    
    Results are sorted by:
    1. Highest rating first
    2. Nearest distance for cafes with same rating
    """
    try:
        logger.info(
            f"Recommendation request by user {current_user.email}: lat={lat}, lng={lng}, radius={radius}, "
            f"min_rating={min_rating}, price_range={price_range}, limit={limit}"
        )
        
        # Parse price ranges
        allowed_price_ranges = parse_price_ranges(price_range)
        
        # Step 1: Search for cafes (BC2)
        cafes = await search_service.search_cafes(
            latitude=lat,
            longitude=lng,
            radius=radius
        )
        
        logger.info(f"Found {len(cafes)} cafes, applying filters...")
        
        # Step 2: Apply recommendation filters and ranking (BC3)
        recommended_cafes = await recommendation_service.get_recommendations(
            cafes=cafes,
            min_rating=min_rating,
            allowed_price_ranges=allowed_price_ranges,
            limit=limit
        )
        
        # Map to response schema
        cafe_responses = [map_cafe_to_response(cafe) for cafe in recommended_cafes]
        
        # Prepare filters applied metadata
        filters_applied = {
            "min_rating": min_rating,
            "price_ranges": [pr.value for pr in allowed_price_ranges] if allowed_price_ranges else None,
            "limit": limit
        }
        
        return RecommendationResponse(
            total=len(cafe_responses),
            cafes=cafe_responses,
            filters_applied=filters_applied
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
