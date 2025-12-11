"""Unit tests for domain models."""
import pytest
from datetime import datetime
from app.domain.models import Cafe, Location, Rating, PriceRange, User


class TestLocation:
    """Test Location value object."""
    
    def test_create_valid_location(self):
        """Test creating a valid location."""
        location = Location(latitude=-6.9175, longitude=107.6191)
        assert location.latitude == -6.9175
        assert location.longitude == 107.6191
    
    def test_location_latitude_bounds(self):
        """Test location latitude boundary validation."""
        # Valid boundaries
        Location(latitude=-90.0, longitude=0.0)
        Location(latitude=90.0, longitude=0.0)
        
        # Invalid boundaries
        with pytest.raises(ValueError):
            Location(latitude=-91.0, longitude=0.0)
        with pytest.raises(ValueError):
            Location(latitude=91.0, longitude=0.0)
    
    def test_location_longitude_bounds(self):
        """Test location longitude boundary validation."""
        # Valid boundaries
        Location(latitude=0.0, longitude=-180.0)
        Location(latitude=0.0, longitude=180.0)
        
        # Invalid boundaries
        with pytest.raises(ValueError):
            Location(latitude=0.0, longitude=-181.0)
        with pytest.raises(ValueError):
            Location(latitude=0.0, longitude=181.0)
    
    def test_location_equality(self):
        """Test location equality comparison."""
        loc1 = Location(latitude=-6.9175, longitude=107.6191)
        loc2 = Location(latitude=-6.9175, longitude=107.6191)
        loc3 = Location(latitude=-6.9180, longitude=107.6195)
        
        assert loc1 == loc2
        assert loc1 != loc3


class TestRating:
    """Test Rating value object."""
    
    def test_create_valid_rating(self):
        """Test creating a valid rating."""
        rating = Rating(value=4.5)
        assert rating.value == 4.5
    
    def test_rating_bounds(self):
        """Test rating boundary validation."""
        # Valid boundaries
        Rating(value=0.0)
        Rating(value=5.0)
        
        # Invalid boundaries
        with pytest.raises(ValueError):
            Rating(value=-0.1)
        with pytest.raises(ValueError):
            Rating(value=5.1)
    
    def test_rating_comparison(self):
        """Test rating comparison operators."""
        rating1 = Rating(value=4.0)
        rating2 = Rating(value=4.5)
        rating3 = Rating(value=4.0)
        
        assert rating1 < rating2
        assert rating2 > rating1
        assert rating1 == rating3
        assert rating1 <= rating3
        assert rating1 >= rating3


class TestPriceRange:
    """Test PriceRange enum."""
    
    def test_all_price_ranges(self):
        """Test all price range values."""
        assert PriceRange.CHEAP.value == "CHEAP"
        assert PriceRange.MEDIUM.value == "MEDIUM"
        assert PriceRange.HIGH.value == "HIGH"
        assert PriceRange.VERY_HIGH.value == "VERY_HIGH"
        assert PriceRange.LUXURY.value == "LUXURY"
        assert PriceRange.UNKNOWN.value == "UNKNOWN"
    
    def test_from_google_price_level(self):
        """Test mapping from Google Places price_level."""
        assert PriceRange.from_google_price_level(0) == PriceRange.CHEAP
        assert PriceRange.from_google_price_level(1) == PriceRange.MEDIUM
        assert PriceRange.from_google_price_level(2) == PriceRange.HIGH
        assert PriceRange.from_google_price_level(3) == PriceRange.VERY_HIGH
        assert PriceRange.from_google_price_level(4) == PriceRange.LUXURY
        assert PriceRange.from_google_price_level(None) == PriceRange.UNKNOWN
        assert PriceRange.from_google_price_level(5) == PriceRange.UNKNOWN


class TestCafe:
    """Test Cafe entity."""
    
    def test_create_valid_cafe(self):
        """Test creating a valid cafe."""
        location = Location(latitude=-6.9175, longitude=107.6191)
        rating = Rating(value=4.5)
        
        cafe = Cafe(
            id="test_id",
            name="Test Cafe",
            address="123 Test St",
            location=location,
            rating=rating,
            price_range=PriceRange.MEDIUM
        )
        
        assert cafe.id == "test_id"
        assert cafe.name == "Test Cafe"
        assert cafe.address == "123 Test St"
        assert cafe.location == location
        assert cafe.rating == rating
        assert cafe.price_range == PriceRange.MEDIUM
        assert cafe.distance_meters is None
    
    def test_cafe_with_distance(self):
        """Test cafe with distance set."""
        location = Location(latitude=-6.9175, longitude=107.6191)
        rating = Rating(value=4.5)
        
        cafe = Cafe(
            id="test_id",
            name="Test Cafe",
            address="123 Test St",
            location=location,
            rating=rating,
            price_range=PriceRange.MEDIUM,
            distance_meters=250.5
        )
        
        assert cafe.distance_meters == 250.5
    
    def test_cafe_equality(self):
        """Test cafe equality based on ID."""
        location = Location(latitude=-6.9175, longitude=107.6191)
        rating = Rating(value=4.5)
        
        cafe1 = Cafe("id1", "Cafe 1", "Address 1", location, rating, PriceRange.CHEAP)
        cafe2 = Cafe("id1", "Different Name", "Different Address", location, rating, PriceRange.HIGH)
        cafe3 = Cafe("id2", "Cafe 1", "Address 1", location, rating, PriceRange.CHEAP)
        
        assert cafe1 == cafe2  # Same ID
        assert cafe1 != cafe3  # Different ID


class TestUser:
    """Test User entity."""
    
    def test_create_valid_user(self):
        """Test creating a valid user."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert isinstance(user.id, str)
        assert isinstance(user.created_at, datetime)
    
    def test_user_email_lowercase(self):
        """Test user email is stored in lowercase."""
        user = User(
            email="Test@Example.COM",
            hashed_password="hashed_password_123"
        )
        assert user.email == "test@example.com"
    
    def test_user_default_active(self):
        """Test user is active by default."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        assert user.is_active is True
    
    def test_user_inactive(self):
        """Test creating inactive user."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            is_active=False
        )
        assert user.is_active is False
    
    def test_user_unique_id(self):
        """Test each user gets a unique ID."""
        user1 = User(email="user1@example.com", hashed_password="pass1")
        user2 = User(email="user2@example.com", hashed_password="pass2")
        
        assert user1.id != user2.id
    
    def test_user_equality(self):
        """Test user equality based on ID."""
        user1 = User(email="test@example.com", hashed_password="pass")
        user2 = User(email="different@example.com", hashed_password="different")
        
        # Force same ID for testing
        user2.id = user1.id
        assert user1 == user2
        
        # Different IDs
        user3 = User(email="test@example.com", hashed_password="pass")
        assert user1 != user3
