"""Unit tests for auth API endpoints."""
import pytest
from fastapi import status


class TestAuthRegister:
    """Test user registration endpoint."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["is_active"] is True
        assert "id" in data["user"]
    
    def test_register_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email fails."""
        # Register first user
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Attempt duplicate registration
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client):
        """Test registration with password shorter than 8 characters."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        # Missing password
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing email
        response = client.post(
            "/api/v1/auth/register",
            json={"password": "securepass123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_empty_body(self, client):
        """Test registration with empty request body."""
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, sample_user_data):
        """Test successful login."""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        response = client.post("/api/v1/auth/login", json=sample_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30 minutes
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client, sample_user_data):
        """Test login with wrong password."""
        # Register user
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_user_data["email"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_case_insensitive_email(self, client, sample_user_data):
        """Test login with different email case."""
        # Register user
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with different case
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_user_data["email"].upper(),
                "password": sample_user_data["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        response = client.post(
            "/api/v1/auth/login",
            json={"password": "password123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthMe:
    """Test get current user endpoint."""
    
    def test_get_me_success(self, client, sample_user_data):
        """Test getting current user info with valid token."""
        # Register and login
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["is_active"] is True
        assert "id" in data
    
    def test_get_me_without_token(self, client):
        """Test accessing /me without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_get_me_invalid_token(self, client):
        """Test accessing /me with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_malformed_auth_header(self, client):
        """Test accessing /me with malformed auth header."""
        # Missing Bearer prefix
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "some_token"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Wrong scheme
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic dXNlcjpwYXNz"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAuthFlow:
    """Test complete authentication flow."""
    
    def test_complete_auth_flow(self, client):
        """Test complete register -> login -> access protected endpoint flow."""
        # 1. Register
        register_data = {
            "email": "flowtest@example.com",
            "password": "testpass123"
        }
        register_response = client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["user"]["id"]
        
        # 2. Login
        login_response = client.post("/api/v1/auth/login", json=register_data)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        
        # 3. Access protected endpoint
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["id"] == user_id
        assert me_response.json()["email"] == register_data["email"]
    
    def test_multiple_users_isolation(self, client):
        """Test that multiple users are properly isolated."""
        # Create user 1
        user1_data = {"email": "user1@example.com", "password": "pass1"}
        client.post("/api/v1/auth/register", json=user1_data)
        user1_login = client.post("/api/v1/auth/login", json=user1_data)
        user1_token = user1_login.json()["access_token"]
        
        # Create user 2
        user2_data = {"email": "user2@example.com", "password": "pass2"}
        client.post("/api/v1/auth/register", json=user2_data)
        user2_login = client.post("/api/v1/auth/login", json=user2_data)
        user2_token = user2_login.json()["access_token"]
        
        # Each token should return correct user
        user1_me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert user1_me.json()["email"] == "user1@example.com"
        
        user2_me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert user2_me.json()["email"] == "user2@example.com"
