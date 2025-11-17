"""
Domain models for the Cafe Recommendation Service.
BC1 (Catalog): Domain entities and value objects representing cafes.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PriceRange(str, Enum):
    """
    Price range enum mapping from Google Places price_level.
    0 → CHEAP, 1 → MEDIUM, 2 → HIGH, 3 → VERY_HIGH, 4 → LUXURY, None → UNKNOWN
    """
    CHEAP = "CHEAP"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    LUXURY = "LUXURY"
    UNKNOWN = "UNKNOWN"
    
    @staticmethod
    def from_google_price_level(price_level: Optional[int]) -> "PriceRange":
        """Convert Google price_level (0-4) to PriceRange enum."""
        mapping = {
            0: PriceRange.CHEAP,
            1: PriceRange.MEDIUM,
            2: PriceRange.HIGH,
            3: PriceRange.VERY_HIGH,
            4: PriceRange.LUXURY,
        }
        return mapping.get(price_level, PriceRange.UNKNOWN) if price_level is not None else PriceRange.UNKNOWN


@dataclass(frozen=True)
class Location:
    """Value object representing geographic coordinates."""
    latitude: float
    longitude: float
    
    def __post_init__(self):
        """Validate coordinates."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")


@dataclass(frozen=True)
class Rating:
    """Value object representing a rating score."""
    value: float
    
    def __post_init__(self):
        """Validate rating is between 0.0 and 5.0."""
        if not 0.0 <= self.value <= 5.0:
            raise ValueError(f"Invalid rating: {self.value}. Must be between 0.0 and 5.0")
    
    def __ge__(self, other) -> bool:
        """Support >= comparison."""
        if isinstance(other, Rating):
            return self.value >= other.value
        elif isinstance(other, (int, float)):
            return self.value >= other
        return NotImplemented
    
    def __gt__(self, other) -> bool:
        """Support > comparison."""
        if isinstance(other, Rating):
            return self.value > other.value
        elif isinstance(other, (int, float)):
            return self.value > other
        return NotImplemented
    
    def __lt__(self, other) -> bool:
        """Support < comparison."""
        if isinstance(other, Rating):
            return self.value < other.value
        elif isinstance(other, (int, float)):
            return self.value < other
        return NotImplemented


@dataclass
class Cafe:
    """
    Entity representing a cafe.
    Mapped from Google Places API data (BC1 - Catalog bounded context).
    """
    id: str  # Google place_id
    name: str
    address: str
    location: Location
    rating: Rating
    price_range: PriceRange
    distance_meters: Optional[float] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.id:
            raise ValueError("Cafe id cannot be empty")
        if not self.name:
            raise ValueError("Cafe name cannot be empty")
