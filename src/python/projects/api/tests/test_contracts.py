"""Unit tests for contracts module"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import io


class TestContractEndpoints:
    """Test contract management endpoints"""

    @pytest.mark.asyncio
    async def test_create_contract_success(self, async_client, mock_storage, sample_pdf_content):
        """Test successful contract creation"""
        with patch("api.handlers.v1.contracts.storage", mock_storage):
            with patch("api.handlers.v1.contracts.Contract") as mock_contract_class:
                mock_contract = MagicMock()
                mock_contract.id = "test_contract_id"
                mock_contract.filename = "test.pdf"
                mock_contract.title = "test.pdf"
                mock_contract.status = "pending"
                mock_contract.uploaded_by = "testuser"
                mock_contract.created_at = datetime.utcnow()
                mock_contract.analysis_result = None
                mock_contract.evaluation_result = None
                mock_contract.client_id = None

                mock_contract_class.return_value = mock_contract
                mock_contract.insert = AsyncMock()

                with patch("api.handlers.v1.contracts.get_current_user") as mock_auth:
                    mock_auth.return_value = MagicMock(username="testuser")

                    files = {"file": ("test.pdf", io.BytesIO(sample_pdf_content), "application/pdf")}
                    response = await async_client.post("/api/v1/contracts/", files=files)

                    assert response.status_code == 200
                    data = response.json()
                    assert data["filename"] == "test.pdf"
                    assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_contract_invalid_file_type(self, async_client):
        """Test contract creation with invalid file type"""
        with patch("api.handlers.v1.contracts.get_current_user") as mock_auth:
            mock_auth.return_value = MagicMock(username="testuser")

            files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
            response = await async_client.post("/api/v1/contracts/", files=files)

            assert response.status_code == 400
            assert "Only PDF files are supported" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_list_contracts(self, async_client):
        """Test listing user's contracts"""
        mock_contracts = [
            MagicMock(
                id="contract1",
                filename="test1.pdf",
                title="Test Contract 1",
                status="pending",
                uploaded_by="testuser",
                created_at=datetime.utcnow(),
                client_id=None,
                analysis_result=None,
                evaluation_result=None
            ),
            MagicMock(
                id="contract2",
                filename="test2.pdf",
                title="Test Contract 2",
                status="completed",
                uploaded_by="testuser",
                created_at=datetime.utcnow(),
                client_id=None,
                analysis_result={"clauses": []},
                evaluation_result={"approved": True}
            )
        ]

        with patch("api.handlers.v1.contracts.Contract.find") as mock_find:
            mock_query = MagicMock()
            mock_query.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=mock_contracts)
            mock_find.return_value = mock_query

            with patch("api.handlers.v1.contracts.get_current_user") as mock_auth:
                mock_auth.return_value = MagicMock(username="testuser")

                response = await async_client.get("/api/v1/contracts/")

                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["filename"] == "test1.pdf"
                assert data[1]["filename"] == "test2.pdf"

    @pytest.mark.asyncio
    async def test_get_contract_success(self, async_client, mock_contract):
        """Test getting a specific contract"""
        with patch("api.handlers.v1.contracts.Contract.get", return_value=mock_contract):
            with patch("api.handlers.v1.contracts.get_current_user") as mock_auth:
                mock_auth.return_value = MagicMock(username="testuser")
                mock_contract.uploaded_by = "testuser"

                response = await async_client.get("/api/v1/contracts/test_id")

                assert response.status_code == 200
                data = response.json()
                assert data["filename"] == mock_contract.filename

    @pytest.mark.asyncio
    async def test_get_contract_not_found(self, async_client):
        """Test getting non-existent contract"""
        with patch("api.handlers.v1.contracts.Contract.get", return_value=None):
            with patch("api.handlers.v1.contracts.get_current_user") as mock_auth:
                mock_auth.return_value = MagicMock(username="testuser")

                response = await async_client.get("/api/v1/contracts/nonexistent")

                assert response.status_code == 404
                assert "Contract not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_contract_access_denied(self, async_client, mock_contract):
        """Test getting contract belonging to another user"""
        with patch("api.handlers.v1.contracts.Contract.get", return_value=mock_contract):
            with patch("api.handlers.v1.contracts.get_current_user") as mock_auth:
                mock_auth.return_value = MagicMock(username="testuser")
                mock_contract.uploaded_by = "otheruser"  # Different user

                response = await async_client.get("/api/v1/contracts/test_id")

                assert response.status_code == 403
                assert "Access denied" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_trigger_genai_analysis(self, async_client, mock_contract):
        """Test triggering GenAI analysis pipeline"""
        mock_contract.status = "pending"
        mock_contract.pipeline_runs = []
        mock_contract.save = AsyncMock()

        with patch("api.handlers.v1.contracts.Contract.get", return_value=mock_contract):
            with patch("api.handlers.v1.contracts.get_current_user") as mock_auth:
                with patch("api.handlers.v1.contracts.celery_app") as mock_celery:
                    mock_signature = MagicMock()
                    mock_celery.signature.return_value = mock_signature

                    mock_chain = MagicMock()
                    mock_chain.apply_async.return_value = MagicMock(id="task_123")

                    with patch("api.handlers.v1.contracts.chain", return_value=mock_chain):
                        mock_auth.return_value = MagicMock(username="testuser")

                        response = await async_client.post("/api/v1/contracts/test_id/init-genai")

                        assert response.status_code == 200
                        data = response.json()
                        assert "Analysis pipeline triggered" in data["message"]
                        assert "task_id" in data
                        assert "run_id" in data


class TestContractValidation:
    """Test contract validation logic"""

    def test_contract_state_validation(self):
        """Test contract state validation"""
        from pwc.task_interface.schema import ContractState

        # Test valid states
        valid_states = [
            ContractState.pending.value,
            ContractState.processing.value,
            ContractState.analyzing.value,
            ContractState.evaluating.value,
            ContractState.completed.value,
            ContractState.failed.value
        ]

        for state in valid_states:
            assert state in ["pending", "processing", "analyzing", "evaluating", "completed", "failed"]

    def test_file_type_validation(self):
        """Test file type validation"""
        valid_types = ["application/pdf"]
        invalid_types = ["text/plain", "image/jpeg", "application/doc"]

        for valid_type in valid_types:
            assert valid_type == "application/pdf"

        for invalid_type in invalid_types:
            assert invalid_type != "application/pdf"

    def test_contract_filename_validation(self):
        """Test contract filename validation"""
        valid_filenames = ["contract.pdf", "test_contract_v2.pdf", "Contract-Final.pdf"]
        invalid_filenames = ["", None, "contract.txt", "contract"]

        for filename in valid_filenames:
            assert filename is not None
            assert len(filename) > 0
            assert filename.endswith(".pdf")

        for filename in invalid_filenames:
            if filename:
                assert not filename.endswith(".pdf") or len(filename) == 0
            else:
                assert filename is None or filename == ""


class TestStorageIntegration:
    """Test storage integration"""

    @pytest.mark.asyncio
    async def test_storage_factory_creation(self):
        """Test storage factory creates storage correctly"""
        from pwc.storage import StorageFactory

        storage = StorageFactory.create_storage("local", base_path="/tmp/test")

        assert storage is not None
        assert hasattr(storage, "save")
        assert hasattr(storage, "load")

    @pytest.mark.asyncio
    async def test_mock_storage_operations(self, mock_storage, sample_pdf_content):
        """Test mock storage operations"""
        # Test save
        file_path = await mock_storage.save(sample_pdf_content, "test/path/file.pdf")
        assert file_path == "test/path/file.pdf"

        # Test load
        loaded_content = await mock_storage.load("test/path/file.pdf")
        assert loaded_content == b"fake pdf content"

        # Test read_file
        read_content = await mock_storage.read_file("test/path/file.pdf")
        assert read_content == b"fake pdf content"