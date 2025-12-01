"""
Authentication router for user registration and login.
Provides endpoints for JWT-based authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.services.auth_service import get_auth_service, AuthService
from app.services.user_service import get_user_service, UserService
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RegisterResponse,
    UserResponse,
    AuthErrorResponse
)
from app.config import Settings, get_settings
from app.api.dependencies import CurrentUser

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User registered successfully"},
        400: {"model": AuthErrorResponse, "description": "Email already registered or validation error"}
    },
    summary="Register a new user",
    description="Create a new user account with email and password. Password must be at least 8 characters."
)
async def register(
    request: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
) -> RegisterResponse:
    """
    Register a new user.
    
    - **email**: Valid email address (must be unique)
    - **password**: Password with minimum 8 characters
    
    Returns created user information.
    """
    # Check if user already exists
    existing_user = user_service.get_user_by_email(request.email)
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = auth_service.hash_password(request.password)
    user = user_service.create_user(
        email=request.email,
        hashed_password=hashed_password
    )
    
    logger.info(f"New user registered: {user.email}")
    
    return RegisterResponse(
        message="User registered successfully",
        user=UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active
        )
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        200: {"description": "Login successful, returns JWT token"},
        401: {"model": AuthErrorResponse, "description": "Invalid credentials"}
    },
    summary="Login and get JWT token",
    description="Authenticate with email and password to receive a JWT access token."
)
async def login(
    request: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
    settings: Settings = Depends(get_settings)
) -> TokenResponse:
    """
    Login to get a JWT access token.
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns JWT access token to be used in Authorization header.
    """
    # Find user by email
    user = user_service.get_user_by_email(request.email)
    if not user:
        logger.warning(f"Login attempt with non-existent email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    if not auth_service.verify_password(request.password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token
    access_token = auth_service.create_access_token(user=user)
    
    logger.info(f"User logged in successfully: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        200: {"description": "Current user information"},
        401: {"model": AuthErrorResponse, "description": "Not authenticated"}
    },
    summary="Get current user",
    description="Get the currently authenticated user's information. Requires valid JWT token."
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active
    )
