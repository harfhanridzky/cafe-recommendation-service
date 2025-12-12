"""Unit tests for RecommendationService."""
import pytest
from app.services.recommendation_service import RecommendationService
from app.domain.models import Cafe, Location, Rating, PriceRange


class TestRecommendationService:
    """Test RecommendationService functionality."""
    
    @pytest.fixture
    def service(self):
        """Create RecommendationService instance."""
        return RecommendationService()
    
    @pytest.fixture
    def sample_cafes(self):
        """Create sample cafes for testing."""
        return [
            Cafe(
                id="cafe1",
                name="Budget Cafe",
                address="Address 1",
                location=Location(latitude=-6.2088, longitude=106.8456),
                rating=Rating(3.5),
                price_range=PriceRange.CHEAP,
                distance_meters=1000.0
            ),
            Cafe(
                id="cafe2",
                name="Premium Cafe",
                address="Address 2",
                location=Location(latitude=-6.2100, longitude=106.8470),
                rating=Rating(4.8),
                price_range=PriceRange.HIGH,
                distance_meters=2000.0
            ),
            Cafe(
                id="cafe3",
                name="Mid-range Cafe",
                address="Address 3",
                location=Location(latitude=-6.2110, longitude=106.8480),
                rating=Rating(4.2),
                price_range=PriceRange.MEDIUM,
                distance_meters=1500.0
            ),
            Cafe(
                id="cafe4",
                name="Nearby Budget",
                address="Address 4",
                location=Location(latitude=-6.2090, longitude=106.8460),
                rating=Rating(4.0),
                price_range=PriceRange.CHEAP,
                distance_meters=500.0
            ),
            Cafe(
                id="cafe5",
                name="Luxury Cafe",
                address="Address 5",
                location=Location(latitude=-6.2120, longitude=106.8490),
                rating=Rating(4.9),
                price_range=PriceRange.VERY_HIGH,
                distance_meters=3000.0
            )
        ]
    
    def test_filter_by_rating_minimum(self, service, sample_cafes):
        """Test filtering cafes by minimum rating."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            min_rating=4.5
        )
        
        assert len(result) == 2
        assert all(cafe.rating.value >= 4.5 for cafe in result)
        assert "Premium Cafe" in [cafe.name for cafe in result]
        assert "Luxury Cafe" in [cafe.name for cafe in result]
    
    def test_filter_by_price_range(self, service, sample_cafes):
        """Test filtering cafes by price range."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            price_range=PriceRange.CHEAP
        )
        
        assert len(result) == 2
        assert all(cafe.price_range == PriceRange.CHEAP for cafe in result)
        assert "Budget Cafe" in [cafe.name for cafe in result]
        assert "Nearby Budget" in [cafe.name for cafe in result]
    
    def test_filter_by_rating_and_price(self, service, sample_cafes):
        """Test filtering by both rating and price range."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            min_rating=4.0,
            price_range=PriceRange.CHEAP
        )
        
        assert len(result) == 1
        assert result[0].name == "Nearby Budget"
        assert result[0].rating.value >= 4.0
        assert result[0].price_range == PriceRange.CHEAP
    
    def test_filter_no_criteria(self, service, sample_cafes):
        """Test filtering without any criteria returns all cafes."""
        result = service.filter_and_rank_cafes(cafes=sample_cafes)
        
        assert len(result) == len(sample_cafes)
        assert result == sample_cafes
    
    def test_filter_no_matches(self, service, sample_cafes):
        """Test filtering with criteria that match no cafes."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            min_rating=5.0
        )
        
        assert len(result) == 0
    
    def test_filter_empty_list(self, service):
        """Test filtering empty cafe list."""
        result = service.filter_and_rank_cafes(
            cafes=[],
            min_rating=4.0
        )
        
        assert result == []
    
    def test_sort_by_rating(self, service, sample_cafes):
        """Test sorting cafes by rating (descending)."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            sort_by="rating"
        )
        
        assert len(result) == len(sample_cafes)
        ratings = [cafe.rating.value for cafe in result]
        assert ratings == sorted(ratings, reverse=True)
        assert result[0].name == "Luxury Cafe"  # 4.9
        assert result[-1].name == "Budget Cafe"  # 3.5
    
    def test_sort_by_distance(self, service, sample_cafes):
        """Test sorting cafes by distance (ascending)."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            sort_by="distance"
        )
        
        assert len(result) == len(sample_cafes)
        distances = [cafe.distance_km for cafe in result]
        assert distances == sorted(distances)
        assert result[0].name == "Nearby Budget"  # 0.5 km
        assert result[-1].name == "Luxury Cafe"  # 3.0 km
    
    def test_sort_by_price(self, service, sample_cafes):
        """Test sorting cafes by price (ascending)."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            sort_by="price"
        )
        
        assert len(result) == len(sample_cafes)
        prices = [cafe.price_range.value for cafe in result]
        assert prices == sorted(prices)
        # CHEAP (1) should come first, VERY_EXPENSIVE (4) last
        assert result[0].price_range == PriceRange.CHEAP
        assert result[-1].price_range == PriceRange.VERY_HIGH
    
    def test_limit_results(self, service, sample_cafes):
        """Test limiting number of recommendations."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            limit=3
        )
        
        assert len(result) == 3
    
    def test_limit_exceeds_available(self, service, sample_cafes):
        """Test limit larger than available cafes."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            limit=100
        )
        
        assert len(result) == len(sample_cafes)
    
    def test_limit_zero(self, service, sample_cafes):
        """Test limit of zero returns empty list."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            limit=0
        )
        
        assert len(result) == 0
    
    def test_combined_filter_sort_limit(self, service, sample_cafes):
        """Test combining filter, sort, and limit."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            min_rating=4.0,
            sort_by="rating",
            limit=2
        )
        
        # Should get top 2 cafes with rating >= 4.0
        assert len(result) == 2
        assert result[0].name == "Luxury Cafe"  # 4.9
        assert result[1].name == "Premium Cafe"  # 4.8
        assert all(cafe.rating.value >= 4.0 for cafe in result)
    
    def test_filter_with_price_and_sort_by_distance(self, service, sample_cafes):
        """Test filtering by price and sorting by distance."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            price_range=PriceRange.CHEAP,
            sort_by="distance"
        )
        
        assert len(result) == 2
        assert result[0].name == "Nearby Budget"  # 0.5 km
        assert result[1].name == "Budget Cafe"  # 1.0 km
        assert all(cafe.price_range == PriceRange.CHEAP for cafe in result)
    
    def test_invalid_sort_by(self, service, sample_cafes):
        """Test invalid sort_by parameter uses default (no sorting)."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            sort_by="invalid_field"
        )
        
        # Should return cafes in original order
        assert result == sample_cafes
    
    def test_rating_boundary_4_0(self, service, sample_cafes):
        """Test filtering with rating exactly at boundary."""
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            min_rating=4.0
        )
        
        assert len(result) == 4
        assert all(cafe.rating.value >= 4.0 for cafe in result)
        assert "Budget Cafe" not in [cafe.name for cafe in result]  # 3.5
    
    def test_multiple_price_ranges(self, service):
        """Test filtering different price ranges."""
        cafes = [
            Cafe("c1", "C1", Location(-6.2088, 106.8456), Rating(4.0), 
                 PriceRange.CHEAP, 50, "A1", 1.0),
            Cafe("c2", "C2", Location(-6.2088, 106.8456), Rating(4.0), 
                 PriceRange.MEDIUM, 50, "A2", 1.0),
            Cafe("c3", "C3", Location(-6.2088, 106.8456), Rating(4.0), 
                 PriceRange.HIGH, 50, "A3", 1.0),
            Cafe("c4", "C4", Location(-6.2088, 106.8456), Rating(4.0), 
                 PriceRange.VERY_HIGH, 50, "A4", 1.0),
        ]
        
        for price in [PriceRange.CHEAP, PriceRange.MEDIUM, 
                      PriceRange.HIGH, PriceRange.VERY_HIGH]:
            result = service.filter_and_rank_cafes(cafes=cafes, price_range=price)
            assert len(result) == 1
            assert result[0].price_range == price
    
    def test_preserve_cafe_immutability(self, service, sample_cafes):
        """Test that filtering doesn't modify original cafes."""
        original_count = len(sample_cafes)
        original_first_name = sample_cafes[0].name
        
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            min_rating=4.5,
            sort_by="rating"
        )
        
        # Original list unchanged
        assert len(sample_cafes) == original_count
        assert sample_cafes[0].name == original_first_name
        
        # Result is different
        assert len(result) != original_count
    
    def test_sort_stability(self, service):
        """Test that sorting is stable for equal values."""
        cafes = [
            Cafe("c1", "Cafe A", Location(-6.2088, 106.8456), Rating(4.0), 
                 PriceRange.MEDIUM, 50, "Addr", 1.0),
            Cafe("c2", "Cafe B", Location(-6.2088, 106.8456), Rating(4.0), 
                 PriceRange.MEDIUM, 50, "Addr", 1.0),
            Cafe("c3", "Cafe C", Location(-6.2088, 106.8456), Rating(4.0), 
                 PriceRange.MEDIUM, 50, "Addr", 1.0),
        ]
        
        result = service.filter_and_rank_cafes(cafes=cafes, sort_by="rating")
        
        # Should maintain original order for equal ratings
        names = [cafe.name for cafe in result]
        assert names == ["Cafe A", "Cafe B", "Cafe C"]
    
    def test_complex_scenario(self, service, sample_cafes):
        """Test complex real-world scenario."""
        # User wants: cheap/moderate cafes, rating >= 3.8, sorted by distance, top 3
        result = service.filter_and_rank_cafes(
            cafes=sample_cafes,
            min_rating=3.8,
            sort_by="distance",
            limit=3
        )
        
        # Filter first: rating >= 3.8 removes "Budget Cafe" (3.5)
        # Sort by distance: 0.5, 1.5, 2.0, 3.0
        # Limit to 3
        assert len(result) == 3
        assert result[0].name == "Nearby Budget"  # 0.5 km
        assert all(cafe.rating.value >= 3.8 for cafe in result)
