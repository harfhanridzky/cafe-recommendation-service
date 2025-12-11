"""
Pytest configuration and fixtures for the entire test suite.
"""
import os
import pytest
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment variables before importing app
os.environ["GOOGLE_API_KEY"] = "test_api_key_for_testing"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_for_testing_12345678"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from app.main import app
from app.services.user_service import UserService, _user_service_instance
from app.services.auth_service import AuthService, _auth_service_instance


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client fixture for testing async endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
def reset_user_service():
    """Reset user service singleton before each test."""
    import app.services.user_service as user_service_module
    import app.services.auth_service as auth_service_module
    
    # Reset both singletons
    user_service_module._user_service_instance = None
    auth_service_module._auth_service_instance = None
    
    yield
    
    # Reset again after test
    user_service_module._user_service_instance = None
    auth_service_module._auth_service_instance = None


@pytest.fixture(scope="function")
def user_service() -> UserService:
    """Fresh UserService instance for each test."""
    from app.services.user_service import get_user_service
    return get_user_service()


@pytest.fixture(scope="function")
def auth_service() -> AuthService:
    """Fresh AuthService instance for each test."""
    from app.services.auth_service import get_auth_service
    return get_auth_service()


@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def create_test_user(user_service, auth_service, sample_user_data):
    """Create a test user and return it."""
    hashed_password = auth_service.hash_password(sample_user_data["password"])
    user = user_service.create_user(
        email=sample_user_data["email"],
        hashed_password=hashed_password
    )
    return user


@pytest.fixture
def auth_headers(create_test_user, auth_service):
    """Generate authentication headers with JWT token."""
    token = auth_service.create_access_token(user=create_test_user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_cafe_data():
    """Sample cafe data for testing."""
    return {
        "place_id": "ChIJ_test_place_id",
        "name": "Test Cafe",
        "formatted_address": "123 Test Street, Test City",
        "geometry": {
            "location": {
                "lat": -6.9175,
                "lng": 107.6191
            }
        },
        "rating": 4.5,
        "price_level": 2,
        "user_ratings_total": 100
    }


@pytest.fixture
def mock_google_places_response(sample_cafe_data):
    """Mock Google Places API response."""
    return {
        "results": [sample_cafe_data],
        "status": "OK"
    }
