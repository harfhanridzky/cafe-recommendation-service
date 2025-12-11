"""Unit tests for recommendations API endpoint."""
import pytest
from fastapi import status


class TestRecommendationsEndpoint:
    """Test /api/v1/recommendations endpoint."""
    
    def test_recommendations_requires_authentication(self, client):
        """Test that recommendations endpoint requires JWT token."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_recommendations_success(self, client, auth_headers):
        """Test successful recommendations with authentication."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_recommendations_invalid_token(self, client):
        """Test recommendations with invalid JWT token."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            },
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_recommendations_required_parameters(self, client, auth_headers):
        """Test that latitude and longitude are required."""
        # Missing latitude
        response = client.get(
            "/api/v1/recommendations",
            params={"longitude": 106.8456},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing longitude
        response = client.get(
            "/api/v1/recommendations",
            params={"latitude": -6.2088},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_recommendations_with_min_rating(self, client, auth_headers):
        """Test recommendations with minimum rating filter."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "min_rating": 4.5
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All recommendations should have rating >= 4.5
        for cafe in data["recommendations"]:
            assert cafe["rating"]["value"] >= 4.5
    
    def test_recommendations_with_price_range(self, client, auth_headers):
        """Test recommendations with price range filter."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "price_range": "moderate"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All recommendations should be moderate price
        for cafe in data["recommendations"]:
            assert cafe["price_range"].lower() == "moderate"
    
    def test_recommendations_with_sort_by_rating(self, client, auth_headers):
        """Test recommendations sorted by rating."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "sort_by": "rating"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check descending order
        if len(data["recommendations"]) > 1:
            ratings = [cafe["rating"]["value"] for cafe in data["recommendations"]]
            assert ratings == sorted(ratings, reverse=True)
    
    def test_recommendations_with_sort_by_distance(self, client, auth_headers):
        """Test recommendations sorted by distance."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "sort_by": "distance"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check ascending order
        if len(data["recommendations"]) > 1:
            distances = [cafe["distance_km"] for cafe in data["recommendations"]]
            assert distances == sorted(distances)
    
    def test_recommendations_with_sort_by_price(self, client, auth_headers):
        """Test recommendations sorted by price."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "sort_by": "price"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check ascending price order
        if len(data["recommendations"]) > 1:
            price_map = {"cheap": 1, "moderate": 2, "expensive": 3, "very_expensive": 4}
            prices = [price_map[cafe["price_range"].lower()] for cafe in data["recommendations"]]
            assert prices == sorted(prices)
    
    def test_recommendations_with_limit(self, client, auth_headers):
        """Test recommendations with result limit."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "limit": 5
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["recommendations"]) <= 5
    
    def test_recommendations_combined_filters(self, client, auth_headers):
        """Test recommendations with multiple filters."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "min_rating": 4.0,
                "price_range": "moderate",
                "sort_by": "distance",
                "limit": 3
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["recommendations"]) <= 3
        for cafe in data["recommendations"]:
            assert cafe["rating"]["value"] >= 4.0
            assert cafe["price_range"].lower() == "moderate"
    
    def test_recommendations_invalid_min_rating(self, client, auth_headers):
        """Test recommendations with invalid min_rating."""
        # Rating > 5
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "min_rating": 6.0
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Rating < 0
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "min_rating": -1.0
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_recommendations_invalid_price_range(self, client, auth_headers):
        """Test recommendations with invalid price_range."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "price_range": "invalid_price"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_recommendations_invalid_sort_by(self, client, auth_headers):
        """Test recommendations with invalid sort_by."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "sort_by": "invalid_field"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_recommendations_invalid_limit(self, client, auth_headers):
        """Test recommendations with invalid limit."""
        # Negative limit
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "limit": -1
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_recommendations_zero_limit(self, client, auth_headers):
        """Test recommendations with zero limit."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "limit": 0
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["recommendations"]) == 0
    
    def test_recommendations_response_structure(self, client, auth_headers):
        """Test structure of recommendations response."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        
        if len(data["recommendations"]) > 0:
            cafe = data["recommendations"][0]
            assert "place_id" in cafe
            assert "name" in cafe
            assert "location" in cafe
            assert "rating" in cafe
            assert "price_range" in cafe
            assert "user_ratings_total" in cafe
            assert "vicinity" in cafe
            assert "distance_km" in cafe
    
    def test_recommendations_boundary_coordinates(self, client, auth_headers):
        """Test recommendations with boundary coordinates."""
        # Max latitude
        response = client.get(
            "/api/v1/recommendations",
            params={"latitude": 90.0, "longitude": 0.0},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Min latitude
        response = client.get(
            "/api/v1/recommendations",
            params={"latitude": -90.0, "longitude": 0.0},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Max longitude
        response = client.get(
            "/api/v1/recommendations",
            params={"latitude": 0.0, "longitude": 180.0},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Min longitude
        response = client.get(
            "/api/v1/recommendations",
            params={"latitude": 0.0, "longitude": -180.0},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_recommendations_with_custom_radius(self, client, auth_headers):
        """Test recommendations with custom radius."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "radius": 5000
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_recommendations_malformed_auth_header(self, client):
        """Test recommendations with malformed auth header."""
        # Missing Bearer prefix
        response = client.get(
            "/api/v1/recommendations",
            params={"latitude": -6.2088, "longitude": 106.8456},
            headers={"Authorization": "some_token"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_recommendations_empty_results(self, client, auth_headers):
        """Test recommendations with no matching cafes."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": 0.0,
                "longitude": 0.0,
                "min_rating": 5.0,  # Very strict filter
                "radius": 100
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)


class TestRecommendationsAuthentication:
    """Test authentication scenarios for recommendations endpoint."""
    
    def test_recommendations_multiple_users(self, client):
        """Test that different users can access recommendations independently."""
        # Create user 1
        user1_data = {"email": "user1@test.com", "password": "pass1"}
        client.post("/api/v1/auth/register", json=user1_data)
        user1_login = client.post("/api/v1/auth/login", json=user1_data)
        user1_token = user1_login.json()["access_token"]
        
        # Create user 2
        user2_data = {"email": "user2@test.com", "password": "pass2"}
        client.post("/api/v1/auth/register", json=user2_data)
        user2_login = client.post("/api/v1/auth/login", json=user2_data)
        user2_token = user2_login.json()["access_token"]
        
        # Both users can access recommendations
        response1 = client.get(
            "/api/v1/recommendations",
            params={"latitude": -6.2088, "longitude": 106.8456},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = client.get(
            "/api/v1/recommendations",
            params={"latitude": -6.2088, "longitude": 106.8456},
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response2.status_code == status.HTTP_200_OK
    
    def test_recommendations_expired_token(self, client):
        """Test recommendations with expired token."""
        # This would require mocking time or using a very short expiry
        # For now, we test with invalid token which has similar effect
        response = client.get(
            "/api/v1/recommendations",
            params={"latitude": -6.2088, "longitude": 106.8456},
            headers={"Authorization": "Bearer expired.token.here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRecommendationsFilterCombinations:
    """Test various filter combinations."""
    
    def test_all_price_ranges(self, client, auth_headers):
        """Test recommendations for each price range."""
        price_ranges = ["cheap", "moderate", "expensive", "very_expensive"]
        
        for price_range in price_ranges:
            response = client.get(
                "/api/v1/recommendations",
                params={
                    "latitude": -6.2088,
                    "longitude": 106.8456,
                    "price_range": price_range
                },
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # All results should match the price range
            for cafe in data["recommendations"]:
                assert cafe["price_range"].lower() == price_range
    
    def test_rating_boundary_values(self, client, auth_headers):
        """Test recommendations with different rating boundaries."""
        ratings = [0.0, 2.5, 4.0, 4.5, 5.0]
        
        for min_rating in ratings:
            response = client.get(
                "/api/v1/recommendations",
                params={
                    "latitude": -6.2088,
                    "longitude": 106.8456,
                    "min_rating": min_rating
                },
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # All results should have rating >= min_rating
            for cafe in data["recommendations"]:
                assert cafe["rating"]["value"] >= min_rating
