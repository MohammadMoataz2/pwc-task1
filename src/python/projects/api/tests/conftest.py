"""Test configuration and fixtures for PWC Contract Analysis API"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
from unittest.mock import AsyncMock, MagicMock

# Test configuration
os.environ["TESTING"] = "True"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/pwc_contracts_test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["STORAGE_TYPE"] = "local"
os.environ["LOCAL_STORAGE_PATH"] = "/tmp/test_storage"

from api.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_ai_client():
    """Mock AI client for testing"""
    mock = MagicMock()

    # Mock analyze_contract response
    mock_clause = MagicMock()
    mock_clause.model_dump.return_value = {
        "type": "payment_terms",
        "content": "Payment within 30 days",
        "confidence": 0.95
    }

    mock_analysis_result = MagicMock()
    mock_analysis_result.clauses = [mock_clause]
    mock_analysis_result.metadata = {"total_pages": 2, "language": "en"}

    mock.analyze_contract = AsyncMock(return_value=mock_analysis_result)

    # Mock evaluate_contract response
    mock_evaluation_result = MagicMock()
    mock_evaluation_result.approved = True
    mock_evaluation_result.reasoning = "Contract meets all requirements"
    mock_evaluation_result.score = 85

    mock.evaluate_contract = AsyncMock(return_value=mock_evaluation_result)

    return mock


@pytest.fixture
def mock_storage():
    """Mock storage for testing"""
    mock = MagicMock()
    mock.save = AsyncMock(return_value="test/path/file.pdf")
    mock.load = AsyncMock(return_value=b"fake pdf content")
    mock.read_file = AsyncMock(return_value=b"fake pdf content")
    return mock


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return b"%PDF-1.4 fake pdf content"


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def test_contract_data():
    """Test contract data"""
    return {
        "filename": "test_contract.pdf",
        "title": "Test Contract",
        "file_path": "test/contracts/test_contract.pdf",
        "file_size": 1024,
        "content_type": "application/pdf"
    }


@pytest.fixture
async def auth_headers(client, test_user_data):
    """Get authorization headers for authenticated requests"""
    # Register user
    client.post("/api/v1/auth/register", json=test_user_data)

    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user_data["username"], "password": test_user_data["password"]}
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_contract():
    """Mock contract object"""
    from bson import ObjectId

    mock = MagicMock()
    mock.id = ObjectId()
    mock.filename = "test_contract.pdf"
    mock.file_path = "test/path/file.pdf"
    mock.created_by = "testuser"
    mock.analysis_result = {
        "clauses": [
            {
                "type": "payment_terms",
                "content": "Payment within 30 days",
                "confidence": 0.95
            }
        ],
        "metadata": {"total_pages": 2}
    }
    mock.save = AsyncMock()
    return mock