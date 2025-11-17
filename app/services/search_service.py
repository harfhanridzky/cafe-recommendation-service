"""
Search service for finding cafes near a location.
BC2 (Search): Orchestrates Google Places API calls and maps to domain models.
"""
from typing import List, Dict, Any
from math import radians, sin, cos, sqrt, atan2
import logging

from app.domain.models import Cafe, Location, Rating, PriceRange
from app.infrastructure.google_places_client import GooglePlacesClient, GooglePlacesAPIError

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for searching cafes near a location.
    BC2: Handles search logic, coordinates with Google Places API, and maps results.
    """
    
    def __init__(self, google_places_client: GooglePlacesClient):
        """
        Initialize search service.
        
        Args:
            google_places_client: Google Places API client instance
        """
        self.google_places_client = google_places_client
    
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1: Latitude of first point
            lng1: Longitude of first point
            lat2: Latitude of second point
            lng2: Longitude of second point
        
        Returns:
            Distance in meters
        """
        # Earth's radius in meters
        R = 6371000
        
        # Convert to radians
        lat1_rad, lng1_rad = radians(lat1), radians(lng1)
        lat2_rad, lng2_rad = radians(lat2), radians(lng2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        # Haversine formula
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    def _map_google_result_to_cafe(
        self, 
        result: Dict[str, Any], 
        user_lat: float, 
        user_lng: float
    ) -> Cafe:
        """
        Map a Google Places API result to a Cafe domain entity.
        BC1 (Catalog): Performs mapping from external API structure to domain model.
        
        Args:
            result: Raw result from Google Places API
            user_lat: User's latitude for distance calculation
            user_lng: User's longitude for distance calculation
        
        Returns:
            Cafe domain entity
        """
        # Extract location
        geometry = result.get("geometry", {})
        location_data = geometry.get("location", {})
        cafe_lat = location_data.get("lat", 0.0)
        cafe_lng = location_data.get("lng", 0.0)
        
        location = Location(latitude=cafe_lat, longitude=cafe_lng)
        
        # Extract rating (default to 0.0 if missing)
        rating_value = result.get("rating", 0.0)
        rating = Rating(value=float(rating_value))
        
        # Extract price level and convert to PriceRange
        price_level = result.get("price_level")
        price_range = PriceRange.from_google_price_level(price_level)
        
        # Calculate distance
        distance = self.calculate_distance(user_lat, user_lng, cafe_lat, cafe_lng)
        
        # Extract other fields
        place_id = result.get("place_id", "")
        name = result.get("name", "Unknown Cafe")
        address = result.get("vicinity", result.get("formatted_address", "Address not available"))
        
        return Cafe(
            id=place_id,
            name=name,
            address=address,
            location=location,
            rating=rating,
            price_range=price_range,
            distance_meters=distance
        )
    
    async def search_cafes(
        self, 
        latitude: float, 
        longitude: float, 
        radius: int = 1000
    ) -> List[Cafe]:
        """
        Search for cafes near a given location.
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            radius: Search radius in meters
        
        Returns:
            List of Cafe domain entities
        
        Raises:
            GooglePlacesAPIError: If the API request fails
        """
        try:
            # Call Google Places API
            results = await self.google_places_client.search_nearby_cafes(
                lat=latitude,
                lng=longitude,
                radius=radius
            )
            
            # Map results to domain entities
            cafes = []
            for result in results:
                try:
                    cafe = self._map_google_result_to_cafe(result, latitude, longitude)
                    cafes.append(cafe)
                except Exception as e:
                    # Log mapping errors but continue processing other results
                    logger.warning(f"Failed to map cafe result: {str(e)}")
                    continue
            
            logger.info(f"Successfully mapped {len(cafes)} cafes from {len(results)} results")
            return cafes
            
        except GooglePlacesAPIError as e:
            logger.error(f"Search failed: {str(e)}")
            raise
