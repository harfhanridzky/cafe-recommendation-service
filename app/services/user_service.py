"""
User service for managing users (in-memory storage).
In production, this would be replaced with a database-backed implementation.
"""
from typing import Dict, Optional
import logging

from app.domain.models import User

logger = logging.getLogger(__name__)


class UserService:
    """
    Service for user management with in-memory storage.
    Note: In production, replace with database persistence.
    """
    
    def __init__(self):
        """Initialize with empty user store."""
        self._users: Dict[str, User] = {}
        self._email_index: Dict[str, str] = {}  # email -> user_id mapping
    
    def create_user(self, email: str, hashed_password: str) -> User:
        """
        Create a new user.
        
        Args:
            email: User's email address
            hashed_password: Already hashed password
        
        Returns:
            Created User entity
        
        Raises:
            ValueError: If email already exists
        """
        if email.lower() in self._email_index:
            raise ValueError(f"User with email {email} already exists")
        
        user = User(
            email=email.lower(),
            hashed_password=hashed_password
        )
        
        self._users[user.id] = user
        self._email_index[email.lower()] = user.id
        
        logger.info(f"Created user: {user.email} (id: {user.id})")
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
        
        Returns:
            User entity or None if not found
        """
        user_id = self._email_index.get(email.lower())
        if user_id:
            return self._users.get(user_id)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User's unique identifier
        
        Returns:
            User entity or None if not found
        """
        return self._users.get(user_id)
    
    def user_exists(self, email: str) -> bool:
        """Check if user with given email exists."""
        return email.lower() in self._email_index


# Global singleton instance (in production, use proper DI)
_user_service_instance: Optional[UserService] = None


def get_user_service() -> UserService:
    """Get or create UserService singleton instance."""
    global _user_service_instance
    if _user_service_instance is None:
        _user_service_instance = UserService()
    return _user_service_instance
