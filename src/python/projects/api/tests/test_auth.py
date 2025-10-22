"""Unit tests for authentication module"""

import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""

    def test_register_user_success(self, client, test_user_data):
        """Test successful user registration"""
        with patch("api.handlers.v1.auth.User.find_one", return_value=AsyncMock(return_value=None)):
            with patch("api.handlers.v1.auth.User.insert", return_value=AsyncMock()):
                response = client.post("/api/v1/auth/register", json=test_user_data)

                assert response.status_code == 200
                data = response.json()
                assert data["username"] == test_user_data["username"]
                assert data["email"] == test_user_data["email"]
                assert data["is_active"] is True

    def test_register_user_duplicate_username(self, client, test_user_data):
        """Test registration with duplicate username"""
        # Mock existing user
        mock_user = AsyncMock()
        mock_user.username = test_user_data["username"]

        with patch("api.handlers.v1.auth.User.find_one", return_value=mock_user):
            response = client.post("/api/v1/auth/register", json=test_user_data)

            assert response.status_code == 400
            assert "Username already registered" in response.json()["detail"]

    def test_register_user_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email"""
        # Mock no username conflict but email conflict
        with patch("api.handlers.v1.auth.User.find_one") as mock_find:
            # First call (username check) returns None, second call (email check) returns user
            mock_find.side_effect = [None, AsyncMock()]

            response = client.post("/api/v1/auth/register", json=test_user_data)

            assert response.status_code == 400
            assert "Email already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user_data):
        """Test successful login"""
        # Mock user
        mock_user = AsyncMock()
        mock_user.username = test_user_data["username"]
        mock_user.hashed_password = "$2b$12$hashedpassword"
        mock_user.is_active = True

        with patch("api.handlers.v1.auth.User.find_one", return_value=mock_user):
            with patch("api.core.security.verify_password", return_value=True):
                with patch("api.core.security.create_access_token", return_value="test_token"):
                    response = client.post(
                        "/api/v1/auth/login",
                        data={"username": test_user_data["username"], "password": test_user_data["password"]}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["access_token"] == "test_token"
                    assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials"""
        # Mock user not found
        with patch("api.handlers.v1.auth.User.find_one", return_value=None):
            response = client.post(
                "/api/v1/auth/login",
                data={"username": test_user_data["username"], "password": "wrongpassword"}
            )

            assert response.status_code == 401
            assert "Incorrect username or password" in response.json()["detail"]

    def test_login_inactive_user(self, client, test_user_data):
        """Test login with inactive user"""
        # Mock inactive user
        mock_user = AsyncMock()
        mock_user.username = test_user_data["username"]
        mock_user.hashed_password = "$2b$12$hashedpassword"
        mock_user.is_active = False

        with patch("api.handlers.v1.auth.User.find_one", return_value=mock_user):
            with patch("api.core.security.verify_password", return_value=True):
                response = client.post(
                    "/api/v1/auth/login",
                    data={"username": test_user_data["username"], "password": test_user_data["password"]}
                )

                assert response.status_code == 400
                assert "Inactive user" in response.json()["detail"]


class TestSecurityModule:
    """Test security utility functions"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        from api.core.security import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_token_creation(self):
        """Test JWT token creation"""
        from api.core.security import create_access_token
        from datetime import timedelta

        # Mock user data
        mock_user = AsyncMock()
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.id = "test_id"

        token = create_access_token(
            user_data=mock_user,
            expires_delta=timedelta(minutes=30)
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_validation(self):
        """Test JWT token validation"""
        from api.core.security import create_access_token, verify_token
        from datetime import timedelta

        # Mock user data
        mock_user = AsyncMock()
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.id = "test_id"

        # Create token
        token = create_access_token(
            user_data=mock_user,
            expires_delta=timedelta(minutes=30)
        )

        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload.get("sub") == "testuser"