"""Unit tests for AuthService."""
import pytest
from datetime import timedelta
from jose import jwt
from app.services.auth_service import AuthService
from app.domain.models import User


class TestAuthService:
    """Test authentication service."""
    
    def test_hash_password(self, auth_service):
        """Test password hashing."""
        password = "testpassword123"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash format
    
    def test_hash_password_different_each_time(self, auth_service):
        """Test password hashing produces different hashes (salt)."""
        password = "testpassword123"
        hash1 = auth_service.hash_password(password)
        hash2 = auth_service.hash_password(password)
        
        assert hash1 != hash2  # Different due to salt
    
    def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(wrong_password, hashed) is False
    
    def test_create_access_token(self, auth_service):
        """Test JWT token creation."""
        user = User(email="test@example.com", hashed_password="hashed")
        token = auth_service.create_access_token(user=user)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token
        payload = jwt.decode(
            token,
            auth_service.settings.JWT_SECRET_KEY,
            algorithms=[auth_service.settings.JWT_ALGORITHM]
        )
        
        assert payload["sub"] == user.id
        assert payload["email"] == user.email
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_create_access_token_custom_expiry(self, auth_service):
        """Test JWT token creation with custom expiry."""
        user = User(email="test@example.com", hashed_password="hashed")
        custom_delta = timedelta(minutes=60)
        token = auth_service.create_access_token(user=user, expires_delta=custom_delta)
        
        payload = jwt.decode(
            token,
            auth_service.settings.JWT_SECRET_KEY,
            algorithms=[auth_service.settings.JWT_ALGORITHM]
        )
        
        # Verify custom expiry was applied (check time difference is reasonable)
        exp_time = payload["exp"]
        iat_time = payload["iat"]
        time_diff = exp_time - iat_time
        
        assert time_diff == 3600  # 60 minutes in seconds
    
    def test_verify_token_valid(self, auth_service):
        """Test token verification with valid token."""
        user = User(email="test@example.com", hashed_password="hashed")
        token = auth_service.create_access_token(user=user)
        
        token_data = auth_service.verify_token(token)
        
        assert token_data is not None
        assert token_data.user_id == user.id
        assert token_data.email == user.email
    
    def test_verify_token_invalid(self, auth_service):
        """Test token verification with invalid token."""
        invalid_token = "invalid.jwt.token"
        
        token_data = auth_service.verify_token(invalid_token)
        
        assert token_data is None
    
    def test_verify_token_malformed(self, auth_service):
        """Test token verification with malformed token."""
        malformed_tokens = [
            "not_a_jwt_token",
            "",
            "a.b",  # Not enough parts
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        for token in malformed_tokens:
            token_data = auth_service.verify_token(token)
            assert token_data is None
    
    def test_verify_token_wrong_secret(self, auth_service):
        """Test token verification with token signed by different secret."""
        user = User(email="test@example.com", hashed_password="hashed")
        
        # Create token with different secret
        wrong_secret_token = jwt.encode(
            {"sub": user.id, "email": user.email},
            "wrong_secret_key",
            algorithm="HS256"
        )
        
        token_data = auth_service.verify_token(wrong_secret_token)
        assert token_data is None
    
    def test_verify_token_missing_required_fields(self, auth_service):
        """Test token verification with missing required fields."""
        # Token without 'sub' field
        token_without_sub = jwt.encode(
            {"email": "test@example.com"},
            auth_service.settings.JWT_SECRET_KEY,
            algorithm=auth_service.settings.JWT_ALGORITHM
        )
        
        token_data = auth_service.verify_token(token_without_sub)
        assert token_data is None
    
    def test_get_token_expiry_seconds(self, auth_service):
        """Test getting token expiry time in seconds."""
        expiry = auth_service.get_token_expiry_seconds()
        
        assert expiry == auth_service.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert expiry == 1800  # 30 minutes default
    
    def test_password_edge_cases(self, auth_service):
        """Test password hashing and verification with edge cases."""
        edge_cases = [
            "a",  # Single character
            "12345678",  # Minimum length
            "a" * 100,  # Long password
            "P@ssw0rd!#$%^&*()",  # Special characters
            "密码测试",  # Unicode characters
            "pass word with spaces"
        ]
        
        for password in edge_cases:
            hashed = auth_service.hash_password(password)
            assert auth_service.verify_password(password, hashed) is True
            assert auth_service.verify_password(password + "x", hashed) is False
