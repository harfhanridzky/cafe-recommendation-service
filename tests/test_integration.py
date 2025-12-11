"""Integration tests for complete user workflows."""
import pytest
from fastapi import status


class TestCompleteUserFlow:
    """Test end-to-end user workflows."""
    
    def test_complete_new_user_journey(self, client):
        """Test complete journey: register -> login -> search -> recommendations."""
        # 1. Register new user
        user_data = {
            "email": "journey@test.com",
            "password": "securepass123"
        }
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["user"]["id"]
        
        # 2. Login
        login_response = client.post("/api/v1/auth/login", json=user_data)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        
        # 3. Verify identity
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["id"] == user_id
        assert me_response.json()["email"] == user_data["email"]
        
        # 4. Search cafes (public endpoint)
        search_response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "radius": 1000
            }
        )
        assert search_response.status_code == status.HTTP_200_OK
        search_data = search_response.json()
        assert "cafes" in search_data
        
        # 5. Get personalized recommendations (protected endpoint)
        recommendations_response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "min_rating": 4.0,
                "sort_by": "rating",
                "limit": 5
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert recommendations_response.status_code == status.HTTP_200_OK
        recommendations_data = recommendations_response.json()
        assert "recommendations" in recommendations_data
        assert len(recommendations_data["recommendations"]) <= 5
    
    def test_unauthorized_access_flow(self, client):
        """Test that unauthorized users cannot access protected resources."""
        # Try to access recommendations without token
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try to access /me without token
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Public search should still work
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456
            }
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_multi_user_concurrent_flow(self, client):
        """Test multiple users can use system concurrently."""
        users = [
            {"email": f"user{i}@test.com", "password": f"pass{i}"}
            for i in range(3)
        ]
        
        tokens = []
        
        # Register and login all users
        for user_data in users:
            # Register
            client.post("/api/v1/auth/register", json=user_data)
            
            # Login
            login_response = client.post("/api/v1/auth/login", json=user_data)
            tokens.append(login_response.json()["access_token"])
        
        # All users can access recommendations independently
        for i, token in enumerate(tokens):
            response = client.get(
                "/api/v1/recommendations",
                params={
                    "latitude": -6.2088,
                    "longitude": 106.8456
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == status.HTTP_200_OK
            
            # Verify correct user
            me_response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert me_response.json()["email"] == users[i]["email"]
    
    def test_search_then_filter_flow(self, client, auth_headers):
        """Test workflow of searching then filtering results."""
        location_params = {
            "latitude": -6.2088,
            "longitude": 106.8456,
            "radius": 2000
        }
        
        # 1. Initial search
        search_response = client.get(
            "/api/v1/search",
            params=location_params
        )
        assert search_response.status_code == status.HTTP_200_OK
        all_cafes = search_response.json()["cafes"]
        
        # 2. Get filtered recommendations
        recommendations_response = client.get(
            "/api/v1/recommendations",
            params={
                **location_params,
                "min_rating": 4.5,
                "price_range": "moderate"
            },
            headers=auth_headers
        )
        assert recommendations_response.status_code == status.HTTP_200_OK
        filtered_cafes = recommendations_response.json()["recommendations"]
        
        # Filtered results should be subset of all results
        assert len(filtered_cafes) <= len(all_cafes)
        
        # All filtered cafes should meet criteria
        for cafe in filtered_cafes:
            assert cafe["rating"]["value"] >= 4.5
            assert cafe["price_range"].lower() == "moderate"
    
    def test_progressive_filtering_flow(self, client, auth_headers):
        """Test progressively applying stricter filters."""
        base_params = {
            "latitude": -6.2088,
            "longitude": 106.8456
        }
        
        # 1. No filters
        response1 = client.get(
            "/api/v1/recommendations",
            params=base_params,
            headers=auth_headers
        )
        count1 = len(response1.json()["recommendations"])
        
        # 2. Add rating filter
        response2 = client.get(
            "/api/v1/recommendations",
            params={**base_params, "min_rating": 4.0},
            headers=auth_headers
        )
        count2 = len(response2.json()["recommendations"])
        
        # 3. Add rating and price filter
        response3 = client.get(
            "/api/v1/recommendations",
            params={
                **base_params,
                "min_rating": 4.0,
                "price_range": "moderate"
            },
            headers=auth_headers
        )
        count3 = len(response3.json()["recommendations"])
        
        # More filters = fewer or equal results
        assert count2 <= count1
        assert count3 <= count2


class TestSearchRadiusIntegration:
    """Test search radius behavior across different scenarios."""
    
    def test_increasing_radius_increases_results(self, client):
        """Test that larger radius generally returns more results."""
        location = {"latitude": -6.2088, "longitude": 106.8456}
        
        # Small radius
        response_small = client.get(
            "/api/v1/search",
            params={**location, "radius": 500}
        )
        
        # Large radius
        response_large = client.get(
            "/api/v1/search",
            params={**location, "radius": 5000}
        )
        
        small_count = len(response_small.json()["cafes"])
        large_count = len(response_large.json()["cafes"])
        
        # Larger radius should have >= results
        assert large_count >= small_count
    
    def test_distance_consistency(self, client):
        """Test that reported distances are consistent with radius."""
        response = client.get(
            "/api/v1/search",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "radius": 1000
            }
        )
        
        cafes = response.json()["cafes"]
        
        # All cafes should be within radius (with some tolerance)
        for cafe in cafes:
            # Convert radius to km and add small tolerance
            max_distance_km = 1000 / 1000 + 0.1  # 1.1 km
            assert cafe["distance_km"] <= max_distance_km


class TestErrorHandling:
    """Test error handling across the application."""
    
    def test_invalid_credentials_flow(self, client):
        """Test handling of invalid credentials throughout flow."""
        # Register user
        user_data = {"email": "error@test.com", "password": "correct123"}
        client.post("/api/v1/auth/register", json=user_data)
        
        # Try login with wrong password
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "error@test.com", "password": "wrong123"}
        )
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try accessing protected route without token
        recommendations_response = client.get(
            "/api/v1/recommendations",
            params={"latitude": -6.2088, "longitude": 106.8456}
        )
        assert recommendations_response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_validation_errors_flow(self, client, auth_headers):
        """Test validation errors across endpoints."""
        # Invalid search coordinates
        response = client.get(
            "/api/v1/search",
            params={"latitude": 91.0, "longitude": 106.8456}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid recommendations parameters
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "min_rating": 6.0  # Invalid rating
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid registration data
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "invalid-email", "password": "short"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDataConsistency:
    """Test data consistency across different endpoints."""
    
    def test_same_location_returns_consistent_results(self, client, auth_headers):
        """Test that same location returns consistent cafe data."""
        params = {
            "latitude": -6.2088,
            "longitude": 106.8456,
            "radius": 1000
        }
        
        # Get results from search endpoint
        search_response = client.get("/api/v1/search", params=params)
        search_cafes = search_response.json()["cafes"]
        
        # Get results from recommendations endpoint
        recommendations_response = client.get(
            "/api/v1/recommendations",
            params=params,
            headers=auth_headers
        )
        recommendations_cafes = recommendations_response.json()["recommendations"]
        
        # Both should return cafe data for same location
        # Recommendations might be filtered, but basic data should be consistent
        if len(search_cafes) > 0 and len(recommendations_cafes) > 0:
            # Check that place_ids exist in both
            search_ids = {cafe["place_id"] for cafe in search_cafes}
            rec_ids = {cafe["place_id"] for cafe in recommendations_cafes}
            
            # Recommendations should be subset of search results
            assert rec_ids.issubset(search_ids) or len(rec_ids) == 0
    
    def test_user_data_consistency(self, client):
        """Test user data consistency across endpoints."""
        user_data = {
            "email": "consistency@test.com",
            "password": "testpass123"
        }
        
        # Register
        register_response = client.post("/api/v1/auth/register", json=user_data)
        registered_user = register_response.json()["user"]
        
        # Login
        login_response = client.post("/api/v1/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        
        # Get user info
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        current_user = me_response.json()
        
        # User data should be consistent
        assert registered_user["id"] == current_user["id"]
        assert registered_user["email"] == current_user["email"]
        assert registered_user["is_active"] == current_user["is_active"]


class TestPerformanceScenarios:
    """Test performance-related scenarios."""
    
    def test_multiple_sequential_searches(self, client):
        """Test multiple sequential searches don't interfere."""
        locations = [
            (-6.2088, 106.8456),
            (-6.2100, 106.8470),
            (-6.2110, 106.8480),
            (-6.2120, 106.8490),
            (-6.2130, 106.8500)
        ]
        
        for lat, lng in locations:
            response = client.get(
                "/api/v1/search",
                params={"latitude": lat, "longitude": lng}
            )
            assert response.status_code == status.HTTP_200_OK
            assert "cafes" in response.json()
    
    def test_large_limit_handling(self, client, auth_headers):
        """Test handling of large limit values."""
        response = client.get(
            "/api/v1/recommendations",
            params={
                "latitude": -6.2088,
                "longitude": 106.8456,
                "limit": 1000  # Large limit
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        # Should not crash, returns available results
