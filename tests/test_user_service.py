"""Unit tests for UserService."""
import pytest
from app.services.user_service import UserService
from app.domain.models import User


class TestUserService:
    """Test user management service."""
    
    def test_create_user(self, user_service):
        """Test creating a new user."""
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        user = user_service.create_user(email=email, hashed_password=hashed_password)
        
        assert user.email == email.lower()
        assert user.hashed_password == hashed_password
        assert user.is_active is True
        assert isinstance(user.id, str)
    
    def test_create_user_email_lowercase(self, user_service):
        """Test user email is converted to lowercase."""
        email = "Test@Example.COM"
        hashed_password = "hashed_password_123"
        
        user = user_service.create_user(email=email, hashed_password=hashed_password)
        
        assert user.email == "test@example.com"
    
    def test_create_user_duplicate_email(self, user_service):
        """Test creating user with duplicate email raises error."""
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        # Create first user
        user_service.create_user(email=email, hashed_password=hashed_password)
        
        # Attempt to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            user_service.create_user(email=email, hashed_password=hashed_password)
    
    def test_create_user_duplicate_case_insensitive(self, user_service):
        """Test duplicate check is case-insensitive."""
        email1 = "test@example.com"
        email2 = "Test@Example.COM"
        hashed_password = "hashed_password_123"
        
        # Create first user
        user_service.create_user(email=email1, hashed_password=hashed_password)
        
        # Attempt to create with different case
        with pytest.raises(ValueError, match="already exists"):
            user_service.create_user(email=email2, hashed_password=hashed_password)
    
    def test_get_user_by_email(self, user_service):
        """Test retrieving user by email."""
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        created_user = user_service.create_user(email=email, hashed_password=hashed_password)
        retrieved_user = user_service.get_user_by_email(email)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    def test_get_user_by_email_case_insensitive(self, user_service):
        """Test retrieving user by email is case-insensitive."""
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        created_user = user_service.create_user(email=email, hashed_password=hashed_password)
        
        # Try different cases
        assert user_service.get_user_by_email("Test@Example.COM") == created_user
        assert user_service.get_user_by_email("TEST@EXAMPLE.COM") == created_user
        assert user_service.get_user_by_email("test@example.com") == created_user
    
    def test_get_user_by_email_not_found(self, user_service):
        """Test retrieving non-existent user returns None."""
        user = user_service.get_user_by_email("nonexistent@example.com")
        assert user is None
    
    def test_get_user_by_id(self, user_service):
        """Test retrieving user by ID."""
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        created_user = user_service.create_user(email=email, hashed_password=hashed_password)
        retrieved_user = user_service.get_user_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    def test_get_user_by_id_not_found(self, user_service):
        """Test retrieving non-existent user by ID returns None."""
        user = user_service.get_user_by_id("non_existent_id")
        assert user is None
    
    def test_user_exists(self, user_service):
        """Test checking if user exists."""
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        # User doesn't exist yet
        assert user_service.user_exists(email) is False
        
        # Create user
        user_service.create_user(email=email, hashed_password=hashed_password)
        
        # User exists now
        assert user_service.user_exists(email) is True
    
    def test_user_exists_case_insensitive(self, user_service):
        """Test user_exists check is case-insensitive."""
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        user_service.create_user(email=email, hashed_password=hashed_password)
        
        assert user_service.user_exists("Test@Example.COM") is True
        assert user_service.user_exists("TEST@EXAMPLE.COM") is True
    
    def test_multiple_users(self, user_service):
        """Test creating and managing multiple users."""
        users_data = [
            ("user1@example.com", "pass1"),
            ("user2@example.com", "pass2"),
            ("user3@example.com", "pass3"),
        ]
        
        created_users = []
        for email, password in users_data:
            user = user_service.create_user(email=email, hashed_password=password)
            created_users.append(user)
        
        # Verify all users can be retrieved
        for user in created_users:
            retrieved = user_service.get_user_by_email(user.email)
            assert retrieved is not None
            assert retrieved.id == user.id
            
            retrieved_by_id = user_service.get_user_by_id(user.id)
            assert retrieved_by_id is not None
            assert retrieved_by_id.email == user.email
    
    def test_user_service_isolation(self):
        """Test that different service instances share state (singleton pattern)."""
        from app.services.user_service import get_user_service
        
        service1 = get_user_service()
        service2 = get_user_service()
        
        # Should be same instance
        assert service1 is service2
        
        # Create user with service1
        user = service1.create_user(email="test@example.com", hashed_password="pass")
        
        # Should be retrievable from service2
        retrieved = service2.get_user_by_email("test@example.com")
        assert retrieved is not None
        assert retrieved.id == user.id
    
    def test_empty_email_handling(self, user_service):
        """Test handling of empty or invalid emails."""
        # These will be caught by Pydantic validation before reaching service
        # But we test service behavior with edge cases
        with pytest.raises(ValueError):
            user_service.create_user(email="", hashed_password="pass")
    
    def test_special_characters_in_email(self, user_service):
        """Test emails with special but valid characters."""
        valid_emails = [
            "user+tag@example.com",
            "user.name@example.com",
            "user_name@example.co.uk",
            "123@example.com",
        ]
        
        for email in valid_emails:
            user = user_service.create_user(email=email, hashed_password="pass")
            assert user.email == email.lower()
            assert user_service.get_user_by_email(email) is not None
