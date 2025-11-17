"""
Recommendation service for filtering and ranking cafes.
BC3 (Recommendation): Applies business rules to filter and sort cafes.
"""
from typing import List, Optional
import logging

from app.domain.models import Cafe, PriceRange

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for filtering and ranking cafes based on user preferences.
    BC3: Applies recommendation logic (filtering by rating/price, sorting).
    """
    
    @staticmethod
    def filter_and_rank_cafes(
        cafes: List[Cafe],
        min_rating: float = 0.0,
        allowed_price_ranges: Optional[List[PriceRange]] = None,
        limit: Optional[int] = None
    ) -> List[Cafe]:
        """
        Filter and rank cafes based on criteria.
        
        Args:
            cafes: List of Cafe entities to filter
            min_rating: Minimum rating threshold (0.0 - 5.0)
            allowed_price_ranges: List of allowed price ranges (None = all)
            limit: Maximum number of results to return (None = no limit)
        
        Returns:
            Filtered and sorted list of Cafe entities
        """
        logger.info(
            f"Filtering {len(cafes)} cafes with min_rating={min_rating}, "
            f"price_ranges={allowed_price_ranges}, limit={limit}"
        )
        
        # Filter by rating
        filtered = [cafe for cafe in cafes if cafe.rating.value >= min_rating]
        logger.debug(f"After rating filter: {len(filtered)} cafes")
        
        # Filter by price range if specified
        if allowed_price_ranges:
            filtered = [
                cafe for cafe in filtered 
                if cafe.price_range in allowed_price_ranges
            ]
            logger.debug(f"After price range filter: {len(filtered)} cafes")
        
        # Sort by rating (descending) then by distance (ascending)
        # Higher rating first, then nearest first for same rating
        sorted_cafes = sorted(
            filtered,
            key=lambda cafe: (
                -cafe.rating.value,  # Negative for descending order
                cafe.distance_meters if cafe.distance_meters is not None else float('inf')
            )
        )
        
        # Apply limit
        if limit and limit > 0:
            sorted_cafes = sorted_cafes[:limit]
        
        logger.info(f"Returning {len(sorted_cafes)} recommended cafes")
        return sorted_cafes
    
    async def get_recommendations(
        self,
        cafes: List[Cafe],
        min_rating: float = 0.0,
        allowed_price_ranges: Optional[List[PriceRange]] = None,
        limit: int = 20
    ) -> List[Cafe]:
        """
        Get cafe recommendations based on filters.
        Async wrapper for filter_and_rank_cafes to match service pattern.
        
        Args:
            cafes: List of cafes from search
            min_rating: Minimum rating threshold
            allowed_price_ranges: Allowed price ranges
            limit: Maximum results
        
        Returns:
            Recommended cafes
        """
        return self.filter_and_rank_cafes(
            cafes=cafes,
            min_rating=min_rating,
            allowed_price_ranges=allowed_price_ranges,
            limit=limit
        )
