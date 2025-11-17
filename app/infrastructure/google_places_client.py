"""
Google Places API client for fetching cafe data.
Infrastructure layer for external API integration.
"""
import httpx
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GooglePlacesAPIError(Exception):
    """Custom exception for Google Places API errors."""
    pass


class GooglePlacesClient:
    """
    Client for interacting with Google Places API.
    Handles nearby search and place details retrieval.
    """
    
    BASE_URL = "https://maps.googleapis.com/maps/api/place"
    
    def __init__(self, api_key: str):
        """
        Initialize the Google Places API client.
        
        Args:
            api_key: Google Places API key
        """
        if not api_key:
            raise ValueError("Google API key is required")
        
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def search_nearby_cafes(
        self, 
        lat: float, 
        lng: float, 
        radius: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Search for cafes near a given location using Google Places Nearby Search API.
        
        Args:
            lat: Latitude of the search center
            lng: Longitude of the search center
            radius: Search radius in meters (default: 1000)
        
        Returns:
            List of cafe data dictionaries from Google Places API
        
        Raises:
            GooglePlacesAPIError: If the API request fails
        """
        url = f"{self.BASE_URL}/nearbysearch/json"
        
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "cafe",
            "key": self.api_key
        }
        
        try:
            logger.info(f"Searching cafes near ({lat}, {lng}) with radius {radius}m")
            # Note: API key is not logged for security
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Google Places API returned status {response.status_code}")
                raise GooglePlacesAPIError(
                    f"Google Places API request failed with status {response.status_code}"
                )
            
            data = response.json()
            
            # Check API response status
            status = data.get("status")
            if status == "ZERO_RESULTS":
                logger.info("No cafes found in the specified area")
                return []
            
            if status not in ["OK", "ZERO_RESULTS"]:
                error_message = data.get("error_message", "Unknown error")
                logger.error(f"Google Places API error: {status} - {error_message}")
                raise GooglePlacesAPIError(
                    f"Google Places API error: {status} - {error_message}"
                )
            
            results = data.get("results", [])
            logger.info(f"Found {len(results)} cafes")
            return results
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during Google Places API request: {str(e)}")
            raise GooglePlacesAPIError(f"HTTP error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during Google Places API request: {str(e)}")
            raise GooglePlacesAPIError(f"Unexpected error: {str(e)}") from e
    
    async def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific place.
        
        Args:
            place_id: Google Place ID
        
        Returns:
            Place details dictionary or None if not found
        
        Raises:
            GooglePlacesAPIError: If the API request fails
        """
        url = f"{self.BASE_URL}/details/json"
        
        params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_address,geometry,price_level,photos",
            "key": self.api_key
        }
        
        try:
            logger.info(f"Fetching details for place_id: {place_id}")
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Google Places API returned status {response.status_code}")
                raise GooglePlacesAPIError(
                    f"Google Places API request failed with status {response.status_code}"
                )
            
            data = response.json()
            
            status = data.get("status")
            if status == "NOT_FOUND":
                logger.warning(f"Place not found: {place_id}")
                return None
            
            if status != "OK":
                error_message = data.get("error_message", "Unknown error")
                logger.error(f"Google Places API error: {status} - {error_message}")
                raise GooglePlacesAPIError(
                    f"Google Places API error: {status} - {error_message}"
                )
            
            result = data.get("result")
            logger.info(f"Successfully fetched details for place_id: {place_id}")
            return result
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during Google Places API request: {str(e)}")
            raise GooglePlacesAPIError(f"HTTP error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during Google Places API request: {str(e)}")
            raise GooglePlacesAPIError(f"Unexpected error: {str(e)}") from e
