"""Simple working tests for PWC Contract Analysis API"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestBasicEndpoints:
    """Test basic API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "PWC Contract Analysis API" in data["message"]

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_register_user(self):
        """Test user registration"""
        user_data = {
            "username": "testuser123",
            "email": "test123@example.com",
            "password": "TestPassword123!"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        # Should work or user already exists
        assert response.status_code in [200, 400]

    def test_login_with_wrong_credentials(self):
        """Test login with wrong credentials"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401


class TestPasswordHashing:
    """Test password utilities"""

    def test_password_hashing(self):
        """Test password hashing works"""
        from api.core.security import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False


class TestOpenAPISpec:
    """Test API specification"""

    def test_openapi_docs(self):
        """Test OpenAPI documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json(self):
        """Test OpenAPI JSON specification"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "info" in data
        assert "paths" in data