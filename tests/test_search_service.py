"""Unit tests for SearchService."""
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.search_service import SearchService
from app.domain.models import Location, Cafe, Rating, PriceRange


class TestSearchService:
    """Test SearchService functionality."""
    
    @pytest.fixture
    def search_service(self):
        """Create SearchService instance with mocked Google Places client."""
        mock_client = Mock()
        service = SearchService(google_places_client=mock_client)
        return service
    
    @pytest.mark.asyncio
    async def test_search_cafes_success(self, search_service, mock_google_places_response):
        """Test successful cafe search."""
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=mock_google_places_response
        )
        
        location = Location(latitude=-6.2088, longitude=106.8456)
        results = await search_service.search_cafes(location=location, radius=1000)
        
        assert len(results) == 2
        assert all(isinstance(cafe, Cafe) for cafe in results)
        assert results[0].name == "Test Cafe 1"
        assert results[1].name == "Test Cafe 2"
        
        # Verify API was called with correct params
        search_service.google_places_client.search_nearby_cafes.assert_called_once_with(
            location=location,
            radius=1000
        )
    
    @pytest.mark.asyncio
    async def test_search_cafes_empty_results(self, search_service):
        """Test search with no results."""
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=[]
        )
        
        location = Location(latitude=0.0, longitude=0.0)
        results = await search_service.search_cafes(location=location)
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_cafes_with_custom_radius(self, search_service, mock_google_places_response):
        """Test search with custom radius."""
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=mock_google_places_response
        )
        
        location = Location(latitude=-6.2088, longitude=106.8456)
        custom_radius = 5000
        
        await search_service.search_cafes(location=location, radius=custom_radius)
        
        search_service.google_places_client.search_nearby_cafes.assert_called_once_with(
            location=location,
            radius=custom_radius
        )
    
    @pytest.mark.asyncio
    async def test_search_cafes_handles_api_error(self, search_service):
        """Test handling of API errors."""
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        location = Location(latitude=-6.2088, longitude=106.8456)
        
        with pytest.raises(Exception, match="API Error"):
            await search_service.search_cafes(location=location)
    
    @pytest.mark.asyncio
    async def test_search_cafes_boundary_coordinates(self, search_service):
        """Test search with boundary latitude/longitude values."""
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=[]
        )
        
        # Test max latitude
        location = Location(latitude=90.0, longitude=0.0)
        results = await search_service.search_cafes(location=location)
        assert results == []
        
        # Test min latitude
        location = Location(latitude=-90.0, longitude=0.0)
        results = await search_service.search_cafes(location=location)
        assert results == []
        
        # Test max longitude
        location = Location(latitude=0.0, longitude=180.0)
        results = await search_service.search_cafes(location=location)
        assert results == []
        
        # Test min longitude
        location = Location(latitude=0.0, longitude=-180.0)
        results = await search_service.search_cafes(location=location)
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_cafes_calculates_distance(self, search_service):
        """Test that cafe distances are calculated correctly."""
        mock_data = [
            {
                "place_id": "cafe1",
                "name": "Cafe 1",
                "rating": 4.5,
                "price_level": 2,
                "user_ratings_total": 100,
                "vicinity": "Address 1",
                "geometry": {
                    "location": {"lat": -6.2088, "lng": 106.8456}
                }
            }
        ]
        
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=mock_data
        )
        
        # Search from same location
        search_location = Location(latitude=-6.2088, longitude=106.8456)
        results = await search_service.search_cafes(location=search_location)
        
        assert len(results) == 1
        # Distance should be very small (same location)
        assert results[0].distance_km < 0.1
    
    @pytest.mark.asyncio
    async def test_search_cafes_with_missing_optional_fields(self, search_service):
        """Test search handles missing optional fields gracefully."""
        mock_data = [
            {
                "place_id": "cafe1",
                "name": "Minimal Cafe",
                # Missing rating, price_level
                "user_ratings_total": 0,
                "vicinity": "Address",
                "geometry": {
                    "location": {"lat": -6.2088, "lng": 106.8456}
                }
            }
        ]
        
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=mock_data
        )
        
        location = Location(latitude=-6.2088, longitude=106.8456)
        results = await search_service.search_cafes(location=location)
        
        assert len(results) == 1
        assert results[0].name == "Minimal Cafe"
    
    @pytest.mark.asyncio
    async def test_search_cafes_default_radius(self, search_service, mock_google_places_response):
        """Test that default radius is used when not specified."""
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=mock_google_places_response
        )
        
        location = Location(latitude=-6.2088, longitude=106.8456)
        await search_service.search_cafes(location=location)
        
        # Verify default radius (1500) is used
        call_args = search_service.google_places_client.search_nearby_cafes.call_args
        assert call_args.kwargs["radius"] == 1500
    
    @pytest.mark.asyncio
    async def test_search_multiple_calls_independent(self, search_service):
        """Test that multiple search calls are independent."""
        mock_response_1 = [
            {
                "place_id": "cafe1",
                "name": "Cafe 1",
                "rating": 4.0,
                "price_level": 1,
                "user_ratings_total": 50,
                "vicinity": "Addr 1",
                "geometry": {"location": {"lat": -6.2088, "lng": 106.8456}}
            }
        ]
        
        mock_response_2 = [
            {
                "place_id": "cafe2",
                "name": "Cafe 2",
                "rating": 5.0,
                "price_level": 3,
                "user_ratings_total": 200,
                "vicinity": "Addr 2",
                "geometry": {"location": {"lat": -6.2100, "lng": 106.8500}}
            }
        ]
        
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            side_effect=[mock_response_1, mock_response_2]
        )
        
        location1 = Location(latitude=-6.2088, longitude=106.8456)
        location2 = Location(latitude=-6.2100, longitude=106.8500)
        
        results1 = await search_service.search_cafes(location=location1)
        results2 = await search_service.search_cafes(location=location2)
        
        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0].name == "Cafe 1"
        assert results2[0].name == "Cafe 2"
    
    @pytest.mark.asyncio
    async def test_search_cafes_large_dataset(self, search_service):
        """Test search with large number of results."""
        # Generate 50 cafes
        mock_data = [
            {
                "place_id": f"cafe{i}",
                "name": f"Cafe {i}",
                "rating": 4.0,
                "price_level": 2,
                "user_ratings_total": 100,
                "vicinity": f"Address {i}",
                "geometry": {
                    "location": {"lat": -6.2088 + (i * 0.001), "lng": 106.8456}
                }
            }
            for i in range(50)
        ]
        
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=mock_data
        )
        
        location = Location(latitude=-6.2088, longitude=106.8456)
        results = await search_service.search_cafes(location=location)
        
        assert len(results) == 50
        assert all(isinstance(cafe, Cafe) for cafe in results)


class TestSearchServiceDataTransformation:
    """Test data transformation in SearchService."""
    
    @pytest.fixture
    def search_service(self):
        """Create SearchService instance."""
        mock_client = Mock()
        return SearchService(google_places_client=mock_client)
    
    @pytest.mark.asyncio
    async def test_transform_rating_to_domain_model(self, search_service):
        """Test rating conversion from Google API to domain model."""
        mock_data = [
            {
                "place_id": "cafe1",
                "name": "Cafe",
                "rating": 4.7,
                "price_level": 2,
                "user_ratings_total": 100,
                "vicinity": "Address",
                "geometry": {"location": {"lat": -6.2088, "lng": 106.8456}}
            }
        ]
        
        search_service.google_places_client.search_nearby_cafes = AsyncMock(
            return_value=mock_data
        )
        
        location = Location(latitude=-6.2088, longitude=106.8456)
        results = await search_service.search_cafes(location=location)
        
        assert results[0].rating.value == 4.7
        assert isinstance(results[0].rating, Rating)
    
    @pytest.mark.asyncio
    async def test_transform_price_level_to_enum(self, search_service):
        """Test price level conversion to PriceRange enum."""
        test_cases = [
            (1, PriceRange.CHEAP),
            (2, PriceRange.MODERATE),
            (3, PriceRange.EXPENSIVE),
            (4, PriceRange.VERY_EXPENSIVE)
        ]
        
        for price_level, expected_enum in test_cases:
            mock_data = [
                {
                    "place_id": "cafe1",
                    "name": "Cafe",
                    "rating": 4.0,
                    "price_level": price_level,
                    "user_ratings_total": 100,
                    "vicinity": "Address",
                    "geometry": {"location": {"lat": -6.2088, "lng": 106.8456}}
                }
            ]
            
            search_service.google_places_client.search_nearby_cafes = AsyncMock(
                return_value=mock_data
            )
            
            location = Location(latitude=-6.2088, longitude=106.8456)
            results = await search_service.search_cafes(location=location)
            
            assert results[0].price_range == expected_enum
