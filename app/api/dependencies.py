"""
API dependencies for authentication and authorization.
Provides reusable JWT middleware/guards for protecting endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
import logging

from app.services.auth_service import get_auth_service, AuthService
from app.services.user_service import get_user_service, UserService
from app.domain.models import User
from app.schemas.auth import TokenData

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT token obtained from the login endpoint",
    auto_error=True
)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    This is the main authentication middleware/guard.
    Use this as a dependency in protected endpoints.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        auth_service: Auth service for token verification
        user_service: User service for user lookup
    
    Returns:
        Authenticated User entity
    
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    # Verify token
    token_data: TokenData = auth_service.verify_token(token)
    if token_data is None:
        logger.warning("Invalid or expired token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from token data
    user = user_service.get_user_by_id(token_data.user_id)
    if user is None:
        logger.warning(f"User not found for token user_id: {token_data.user_id}")
        raise credentials_exception
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Authenticated user: {user.email}")
    return user


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))],
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
) -> User | None:
    """
    Optional dependency to get the current user if token is provided.
    Returns None if no token or invalid token.
    
    Use this for endpoints that work both with and without authentication.
    """
    if credentials is None:
        return None
    
    token_data = auth_service.verify_token(credentials.credentials)
    if token_data is None:
        return None
    
    user = user_service.get_user_by_id(token_data.user_id)
    if user is None or not user.is_active:
        return None
    
    return user


# Type alias for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
