"""Unit tests for search API endpoint."""
import pytest
from fastapi import status


class TestSearchEndpoint:
    """Test /api/v1/search endpoint."""
    
    def test_search_success(self, client, mock_google_places_response):
        """Test successful cafe search."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "radius": 1000
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "cafes" in data
        assert isinstance(data["cafes"], list)
        assert len(data["cafes"]) >= 0
    
    def test_search_required_parameters(self, client):
        """Test that latitude and longitude are required."""
        # Missing latitude
        response = client.get(
            "/api/v1/search",
            params={"longitude": 106.8456}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing longitude
        response = client.get(
            "/api/v1/search",
            params={"latitude": -6.2088}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing both
        response = client.get("/api/v1/search")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_search_with_default_radius(self, client):
        """Test search uses default radius when not specified."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        # Should work with default radius
    
    def test_search_custom_radius(self, client):
        """Test search with custom radius."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "radius": 5000
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_invalid_latitude(self, client):
        """Test search with invalid latitude values."""
        # Latitude > 90
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": 91.0,
                "longitude": 106.8456
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Latitude < -90
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -91.0,
                "longitude": 106.8456
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_search_invalid_longitude(self, client):
        """Test search with invalid longitude values."""
        # Longitude > 180
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 181.0
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Longitude < -180
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": -181.0
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_search_boundary_coordinates(self, client):
        """Test search with boundary coordinate values."""
        # Max latitude
        response = client.get(
            "/api/v1/search",
            params={"latitude": 90.0, "longitude": 0.0}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Min latitude
        response = client.get(
            "/api/v1/search",
            params={"latitude": -90.0, "longitude": 0.0}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Max longitude
        response = client.get(
            "/api/v1/search",
            params={"latitude": 0.0, "longitude": 180.0}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Min longitude
        response = client.get(
            "/api/v1/search",
            params={"latitude": 0.0, "longitude": -180.0}
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_invalid_radius(self, client):
        """Test search with invalid radius values."""
        # Negative radius
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "radius": -100
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Zero radius
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "radius": 0
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_search_max_radius(self, client):
        """Test search with maximum allowed radius."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "radius": 50000  # 50km
            }
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_response_structure(self, client):
        """Test the structure of search response."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "cafes" in data
        assert isinstance(data["cafes"], list)
        
        # If cafes exist, check structure
        if len(data["cafes"]) > 0:
            cafe = data["cafes"][0]
            assert "place_id" in cafe
            assert "name" in cafe
            assert "location" in cafe
            assert "rating" in cafe
            assert "price_range" in cafe
            assert "user_ratings_total" in cafe
            assert "vicinity" in cafe
            assert "distance_km" in cafe
    
    def test_search_empty_results(self, client):
        """Test search that returns no results."""
        # Use remote coordinates unlikely to have cafes nearby
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": 0.0,
                "longitude": 0.0,
                "radius": 100
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cafes" in data
        # Empty list is valid response
        assert isinstance(data["cafes"], list)
    
    def test_search_string_coordinates(self, client):
        """Test search with string coordinate values."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": "-6.2088",
                "longitude": "106.8456"
            }
        )
        
        # Should accept string numbers and convert
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_invalid_coordinate_types(self, client):
        """Test search with non-numeric coordinates."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": "invalid",
                "longitude": "106.8456"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": "-6.2088",
                "longitude": "invalid"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_search_decimal_precision(self, client):
        """Test search with high precision coordinates."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.208812345,
                "longitude": 106.845678901
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_no_authentication_required(self, client):
        """Test that search endpoint doesn't require authentication."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            }
        )
        
        # Should work without auth token
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_multiple_requests(self, client):
        """Test multiple independent search requests."""
        locations = [
            (-6.2088, 106.8456),
            (-6.2100, 106.8470),
            (-6.2110, 106.8480)
        ]
        
        for lat, lng in locations:
            response = client.get(
                "/api/v1/search",
                params={"latitude": lat, "longitude": lng}
            )
            assert response.status_code == status.HTTP_200_OK
            assert "cafes" in response.json()
    
    def test_search_extra_parameters_ignored(self, client):
        """Test that extra query parameters are ignored."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "extra_param": "should_be_ignored",
                "another": 123
            }
        )
        
        # Should still work, ignoring extra params
        assert response.status_code == status.HTTP_200_OK


class TestSearchEdgeCases:
    """Test edge cases for search endpoint."""
    
    def test_search_equator_prime_meridian(self, client):
        """Test search at 0,0 coordinates."""
        response = client.get(
            "/api/v1/search",
            params={"latitude": 0.0, "longitude": 0.0}
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_international_date_line(self, client):
        """Test search near international date line."""
        response = client.get(
            "/api/v1/search",
            params={"latitude": 0.0, "longitude": 179.9}
        )
        assert response.status_code == status.HTTP_200_OK
        
        response = client.get(
            "/api/v1/search",
            params={"latitude": 0.0, "longitude": -179.9}
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_poles(self, client):
        """Test search at north and south poles."""
        # North pole
        response = client.get(
            "/api/v1/search",
            params={"latitude": 90.0, "longitude": 0.0}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # South pole
        response = client.get(
            "/api/v1/search",
            params={"latitude": -90.0, "longitude": 0.0}
        )
        assert response.status_code == status.HTTP_200_OK
