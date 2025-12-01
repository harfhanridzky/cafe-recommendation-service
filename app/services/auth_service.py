"""
Authentication service for JWT token management and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.domain.models import User
from app.schemas.auth import TokenData

logger = logging.getLogger(__name__)

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Service for authentication operations.
    Handles password hashing, verification, and JWT token management.
    """
    
    def __init__(self):
        """Initialize auth service with settings."""
        self.settings = get_settings()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored password hash
        
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        user: User, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token for a user.
        
        Args:
            user: User entity to create token for
            expires_delta: Optional custom expiration time
        
        Returns:
            Encoded JWT token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode = {
            "sub": user.id,
            "email": user.email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM
        )
        
        logger.info(f"Created access token for user: {user.email}")
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string to verify
        
        Returns:
            TokenData with user info if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM]
            )
            
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None:
                logger.warning("Token verification failed: missing user_id")
                return None
            
            return TokenData(user_id=user_id, email=email)
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
    
    def get_token_expiry_seconds(self) -> int:
        """Get token expiration time in seconds."""
        return self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


# Global singleton instance
_auth_service_instance: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get or create AuthService singleton instance."""
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance
