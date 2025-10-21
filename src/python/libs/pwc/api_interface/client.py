import httpx
import asyncio
from typing import Optional, Dict, Any
import logging
from pathlib import Path

from ..task_interface.schema import (
    ContractState,
    ContractAnalysisResult,
    ContractEvaluationResult,
    ContractProcessingStatus
)


class APIClient:
    """HTTP client for workers to communicate with internal API endpoints"""

    def __init__(self, base_url: str, auth_token: str, logger: Optional[logging.Logger] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.logger = logger or logging.getLogger(__name__)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=30.0
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()

    def _get_url(self, path: str) -> str:
        return f"{self.base_url}/contracts/{path}"

    async def _make_request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Make HTTP request with error handling and retries"""
        url = self._get_url(path)

        for attempt in range(3):  # 3 retry attempts
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == 2:  # Last attempt
                    raise
                await asyncio.sleep(1)  # Wait before retry

    async def is_pipeline_latest(self, contract_id: str, run_id: str) -> bool:
        """Check if the pipeline run is the latest for this contract"""
        try:
            response = await self._make_request(
                "GET",
                f"{contract_id}/internal/pipeline/{run_id}/is-latest"
            )
            return response.json().get("is_latest", False)
        except Exception as e:
            self.logger.error(f"Failed to check pipeline status: {e}")
            return False

    async def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """Get contract details"""
        response = await self._make_request("GET", f"{contract_id}/internal")
        return response.json()

    async def update_contract_state(
        self,
        contract_id: str,
        state: ContractState,
        run_id: Optional[str] = None
    ):
        """Update contract processing state"""
        params = {"state": state.value}
        if run_id:
            params["run_id"] = run_id

        await self._make_request(
            "PUT",
            f"{contract_id}/internal/change-state",
            params=params
        )
        self.logger.info(f"Updated contract {contract_id} state to {state.value}")

    async def save_analysis_result(
        self,
        contract_id: str,
        result: ContractAnalysisResult
    ):
        """Save contract analysis result"""
        await self._make_request(
            "POST",
            f"{contract_id}/internal/set-analysis-result",
            json=result.dict()
        )
        self.logger.info(f"Saved analysis result for contract {contract_id}")

    async def save_evaluation_result(
        self,
        contract_id: str,
        result: ContractEvaluationResult
    ):
        """Save contract evaluation result"""
        await self._make_request(
            "POST",
            f"{contract_id}/internal/set-evaluation-result",
            json=result.dict()
        )
        self.logger.info(f"Saved evaluation result for contract {contract_id}")

    async def report_failure(
        self,
        contract_id: str,
        error_message: str,
        error_type: str = "processing_error"
    ):
        """Report task failure"""
        await self._make_request(
            "PUT",
            f"{contract_id}/internal/failed",
            json={"error_message": error_message, "error_type": error_type}
        )
        self.logger.error(f"Reported failure for contract {contract_id}: {error_message}")

    async def ping(self) -> bool:
        """Health check for API connectivity"""
        try:
            response = await self.client.get(f"{self.base_url}/healthz")
            return response.status_code == 200
        except Exception:
            return False