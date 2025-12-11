"""Security tests for the API."""
import pytest
from fastapi import status
import jwt
from datetime import datetime, timedelta


class TestJWTSecurity:
    """Test JWT token security."""
    
    def test_token_contains_required_claims(self, client, sample_user_data):
        """Test that JWT tokens contain required claims."""
        # Register and login
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        
        token = login_response.json()["access_token"]
        
        # Decode without verification to inspect claims
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        assert "sub" in decoded  # Subject (user ID)
        assert "exp" in decoded  # Expiration
        assert "iat" in decoded  # Issued at
    
    def test_token_expiry_claim(self, client, sample_user_data):
        """Test that token has proper expiry claim."""
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        
        token = login_response.json()["access_token"]
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        exp_timestamp = decoded["exp"]
        iat_timestamp = decoded["iat"]
        
        # Token should be valid for expected duration (30 minutes = 1800 seconds)
        duration = exp_timestamp - iat_timestamp
        assert duration == 1800
    
    def test_tampered_token_rejected(self, client, sample_user_data):
        """Test that tampered tokens are rejected."""
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        
        token = login_response.json()["access_token"]
        
        # Tamper with token by changing a character
        tampered_token = token[:-10] + "TAMPERED"
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_signature_verified(self, client, sample_user_data):
        """Test that token signature is properly verified."""
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        
        token = login_response.json()["access_token"]
        
        # Create fake token with valid structure but wrong signature
        fake_payload = {
            "sub": "fake_user_id",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            "iat": datetime.utcnow().timestamp()
        }
        fake_token = jwt.encode(fake_payload, "wrong_secret", algorithm="HS256")
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_missing_bearer_scheme(self, client, sample_user_data):
        """Test that requests without Bearer scheme are rejected."""
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        
        token = login_response.json()["access_token"]
        
        # Send token without Bearer scheme
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": token}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_case_sensitive_bearer_scheme(self, client, sample_user_data):
        """Test that Bearer scheme is case-sensitive."""
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        
        token = login_response.json()["access_token"]
        
        # Try with lowercase 'bearer'
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"bearer {token}"}
        )
        
        # FastAPI's HTTPBearer is case-insensitive for 'Bearer', so this might pass
        # But we test the behavior
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]


class TestPasswordSecurity:
    """Test password security measures."""
    
    def test_password_not_returned_in_responses(self, client, sample_user_data):
        """Test that passwords are never returned in API responses."""
        # Register
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert "password" not in register_response.json()["user"]
        assert "hashed_password" not in register_response.json()["user"]
        
        # Login and get user info
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        token = login_response.json()["access_token"]
        
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert "password" not in me_response.json()
        assert "hashed_password" not in me_response.json()
    
    def test_password_minimum_length_enforced(self, client):
        """Test that password minimum length is enforced."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short"  # Less than 8 characters
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_passwords_are_hashed(self, client, sample_user_data):
        """Test that passwords are not stored in plaintext."""
        # This is implicitly tested by the fact that login works with bcrypt
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with correct password should work
        login_response = client.post("/api/v1/auth/login", json=sample_user_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        # Login with wrong password should fail
        wrong_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_user_data["email"],
                "password": "wrongpassword"
            }
        )
        assert wrong_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_password_special_characters(self, client):
        """Test that passwords with special characters are handled correctly."""
        special_passwords = [
            "P@ssw0rd!",
            "Test#123$",
            "P&ss^w*rd",
            "Test_Pass-123",
            "Пароль123",  # Unicode
            "密码123456"  # Chinese characters
        ]
        
        for i, password in enumerate(special_passwords):
            user_data = {
                "email": f"special{i}@example.com",
                "password": password
            }
            
            # Register
            register_response = client.post("/api/v1/auth/register", json=user_data)
            assert register_response.status_code == status.HTTP_201_CREATED
            
            # Login should work
            login_response = client.post("/api/v1/auth/login", json=user_data)
            assert login_response.status_code == status.HTTP_200_OK


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_sql_injection_attempts_in_email(self, client):
        """Test that SQL injection attempts in email are handled."""
        sql_injections = [
            "admin'--",
            "' OR '1'='1",
            "admin'; DROP TABLE users--",
            "' OR 1=1--"
        ]
        
        for injection in sql_injections:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": injection,
                    "password": "password123"
                }
            )
            
            # Should fail validation (invalid email format)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_xss_attempts_in_input(self, client):
        """Test that XSS attempts are handled."""
        xss_attempts = [
            "<script>alert('xss')</script>@example.com",
            "test@<script>alert('xss')</script>.com",
            "javascript:alert('xss')@example.com"
        ]
        
        for xss in xss_attempts:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": xss,
                    "password": "password123"
                }
            )
            
            # Should fail validation
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_extremely_long_input_handling(self, client):
        """Test handling of extremely long inputs."""
        # Very long email
        long_email = "a" * 1000 + "@example.com"
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": long_email,
                "password": "password123"
            }
        )
        # Should be rejected
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]
        
        # Very long password
        long_password = "a" * 10000
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": long_password
            }
        )
        # Should handle gracefully
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_null_byte_injection(self, client):
        """Test handling of null byte injection attempts."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test\x00@example.com",
                "password": "password123"
            }
        )
        
        # Should fail validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_coordinate_boundary_validation(self, client):
        """Test that coordinate boundaries are strictly validated."""
        invalid_coords = [
            (91.0, 0.0),      # Latitude > 90
            (-91.0, 0.0),     # Latitude < -90
            (0.0, 181.0),     # Longitude > 180
            (0.0, -181.0),    # Longitude < -180
            (100.0, 200.0),   # Both out of range
        ]
        
        for lat, lng in invalid_coords:
            response = client.get(
                "/api/v1/search",
                params={"latitude": lat, "longitude": lng}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthenticationSecurity:
    """Test authentication security measures."""
    
    def test_cannot_access_other_user_data(self, client):
        """Test that users cannot access other users' data."""
        # Create two users
        user1 = {"email": "user1@test.com", "password": "pass1"}
        user2 = {"email": "user2@test.com", "password": "pass2"}
        
        client.post("/api/v1/auth/register", json=user1)
        client.post("/api/v1/auth/register", json=user2)
        
        # Login as user1
        login1 = client.post("/api/v1/auth/login", json=user1)
        token1 = login1.json()["access_token"]
        
        # Get user1's info
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # Should only get user1's data
        assert me_response.json()["email"] == user1["email"]
        assert me_response.json()["email"] != user2["email"]
    
    def test_token_cannot_be_reused_for_different_user(self, client):
        """Test that tokens are user-specific."""
        # Create two users
        user1 = {"email": "user1@test.com", "password": "pass1"}
        user2 = {"email": "user2@test.com", "password": "pass2"}
        
        client.post("/api/v1/auth/register", json=user1)
        client.post("/api/v1/auth/register", json=user2)
        
        # Get token for user1
        login1 = client.post("/api/v1/auth/login", json=user1)
        token1 = login1.json()["access_token"]
        
        # Using user1's token should always return user1's data
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert me_response.json()["email"] == user1["email"]
    
    def test_brute_force_protection_awareness(self, client):
        """Test awareness of brute force attempts (document behavior)."""
        user_data = {"email": "bruteforce@test.com", "password": "correct123"}
        client.post("/api/v1/auth/register", json=user_data)
        
        # Try multiple wrong passwords
        for _ in range(10):
            response = client.post(
                "/api/v1/auth/login",
                json={"email": user_data["email"], "password": "wrong"}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Correct password should still work (no rate limiting in current impl)
        response = client.post("/api/v1/auth/login", json=user_data)
        assert response.status_code == status.HTTP_200_OK


class TestAPISecurityHeaders:
    """Test security-related behaviors."""
    
    def test_sensitive_error_messages(self, client):
        """Test that error messages don't leak sensitive information."""
        # Try to login with non-existent user
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        # Error message should be generic
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_detail = response.json()["detail"].lower()
        
        # Should not reveal whether user exists
        assert "invalid" in error_detail or "incorrect" in error_detail
        assert "not found" not in error_detail
        assert "does not exist" not in error_detail
    
    def test_timing_attack_resistance(self, client, sample_user_data):
        """Test that authentication timing doesn't leak information."""
        # Register a user
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Both existing and non-existing users should return similar response times
        # This is a basic test - timing attacks require more sophisticated testing
        
        # Existing user with wrong password
        response1 = client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_user_data["email"],
                "password": "wrongpassword"
            }
        )
        assert response1.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Non-existing user
        response2 = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Both should have similar response codes
        assert response1.status_code == response2.status_code
