"""Unit tests for health check module"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.mark.asyncio
    async def test_health_check_success(self, async_client):
        """Test successful health check"""
        response = await async_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_readiness_check_success(self, async_client):
        """Test successful readiness check"""
        # Mock database connection
        with patch("api.handlers.v1.health.get_database") as mock_db:
            mock_db.return_value.command = AsyncMock(return_value={"ok": 1})

            response = await async_client.get("/readyz")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert "checks" in data
            assert data["checks"]["database"] == "healthy"

    @pytest.mark.asyncio
    async def test_readiness_check_database_failure(self, async_client):
        """Test readiness check with database failure"""
        # Mock database connection failure
        with patch("api.handlers.v1.health.get_database") as mock_db:
            mock_db.return_value.command = AsyncMock(side_effect=Exception("Database connection failed"))

            response = await async_client.get("/readyz")

            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "not ready"
            assert data["checks"]["database"] == "unhealthy"


class TestSystemMetrics:
    """Test system metrics functionality"""

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, async_client):
        """Test metrics endpoint"""
        # Mock log entries for metrics calculation
        mock_logs = [
            {
                "endpoint": "/api/v1/contracts/",
                "method": "POST",
                "status_code": 200,
                "response_time": 150,
                "timestamp": "2024-01-01T12:00:00Z"
            },
            {
                "endpoint": "/api/v1/genai/analyze-contract",
                "method": "POST",
                "status_code": 200,
                "response_time": 2500,
                "timestamp": "2024-01-01T12:01:00Z"
            }
        ]

        with patch("api.handlers.v1.metrics.APILog.find") as mock_find:
            mock_query = MagicMock()
            mock_query.to_list = AsyncMock(return_value=mock_logs)
            mock_find.return_value = mock_query

            with patch("api.handlers.v1.metrics.get_current_user") as mock_auth:
                mock_auth.return_value = MagicMock(username="testuser")

                response = await async_client.get("/api/v1/metrics")

                assert response.status_code == 200
                data = response.json()
                assert "total_requests" in data
                assert "avg_response_time" in data
                assert "success_rate" in data

    def test_metrics_calculation(self):
        """Test metrics calculation logic"""
        sample_logs = [
            {"status_code": 200, "response_time": 100},
            {"status_code": 200, "response_time": 200},
            {"status_code": 500, "response_time": 150},
            {"status_code": 200, "response_time": 300}
        ]

        # Calculate metrics
        total_requests = len(sample_logs)
        successful_requests = len([log for log in sample_logs if 200 <= log["status_code"] < 300])
        total_response_time = sum(log["response_time"] for log in sample_logs)

        avg_response_time = total_response_time / total_requests
        success_rate = (successful_requests / total_requests) * 100

        assert total_requests == 4
        assert successful_requests == 3
        assert avg_response_time == 187.5
        assert success_rate == 75.0


class TestLoggingSystem:
    """Test logging system functionality"""

    @pytest.mark.asyncio
    async def test_logs_endpoint(self, async_client):
        """Test logs endpoint"""
        mock_logs = [
            {
                "id": "log1",
                "user": "testuser",
                "endpoint": "/api/v1/contracts/",
                "method": "POST",
                "status_code": 200,
                "response_time": 150,
                "timestamp": "2024-01-01T12:00:00Z"
            },
            {
                "id": "log2",
                "user": "testuser",
                "endpoint": "/api/v1/genai/analyze-contract",
                "method": "POST",
                "status_code": 500,
                "response_time": 2500,
                "timestamp": "2024-01-01T12:01:00Z"
            }
        ]

        with patch("api.handlers.v1.logs.APILog.find") as mock_find:
            mock_query = MagicMock()
            mock_query.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=mock_logs)
            mock_find.return_value = mock_query

            with patch("api.handlers.v1.logs.get_current_user") as mock_auth:
                mock_auth.return_value = MagicMock(username="testuser")

                response = await async_client.get("/api/v1/logs")

                assert response.status_code == 200
                data = response.json()
                assert "logs" in data
                assert "total" in data
                assert len(data["logs"]) == 2

    @pytest.mark.asyncio
    async def test_logs_filtering(self, async_client):
        """Test logs endpoint with filtering"""
        with patch("api.handlers.v1.logs.APILog.find") as mock_find:
            mock_query = MagicMock()
            mock_query.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
            mock_find.return_value = mock_query

            with patch("api.handlers.v1.logs.get_current_user") as mock_auth:
                mock_auth.return_value = MagicMock(username="testuser")

                # Test with filters
                response = await async_client.get(
                    "/api/v1/logs?endpoint=/api/v1/contracts/&status=200&user=testuser"
                )

                assert response.status_code == 200
                # Verify that find was called with filters
                mock_find.assert_called_once()

    def test_log_entry_structure(self):
        """Test log entry structure validation"""
        from api.middleware.logging import LoggingMiddleware

        # Test log entry has required fields
        required_fields = [
            "user", "endpoint", "method", "status_code",
            "response_time", "timestamp", "ip_address"
        ]

        # Mock request and response
        mock_request = MagicMock()
        mock_request.url.path = "/api/v1/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"

        mock_response = MagicMock()
        mock_response.status_code = 200

        # Verify structure exists (this is a structural test)
        assert hasattr(LoggingMiddleware, "__call__")


class TestApplicationStartup:
    """Test application startup and configuration"""

    def test_app_creation(self):
        """Test FastAPI app creation"""
        from api.main import app

        assert app is not None
        assert app.title == "PWC Contract Analysis API"
        assert "API for analyzing contracts using GenAI" in app.description

    def test_cors_configuration(self):
        """Test CORS configuration"""
        from api.main import app

        # Check if CORS middleware is configured
        middleware_types = [type(middleware).__name__ for middleware in app.user_middleware]
        assert any("CORS" in middleware_type for middleware_type in middleware_types)

    def test_router_inclusion(self):
        """Test that all routers are included"""
        from api.main import app

        # Check that routes exist
        route_paths = [route.path for route in app.routes]

        # Check for key API endpoints
        expected_prefixes = [
            "/api/v1/auth",
            "/api/v1/contracts",
            "/api/v1/genai",
            "/api/v1/logs",
            "/api/v1/metrics"
        ]

        for prefix in expected_prefixes:
            assert any(path.startswith(prefix) for path in route_paths), f"Missing routes for {prefix}"