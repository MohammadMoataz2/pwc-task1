from typing import Optional, List
import httpx
from .task_interface import ContractDocument, ContractState, ContractAnalysisResultDB, ContractEvaluationResultDB


class APIClient:
    """Client for communicating with the PWC Contract Analysis API"""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self._headers = {"Content-Type": "application/json"}
        if auth_token:
            self._headers["Authorization"] = f"Bearer {auth_token}"

    async def get_contract(self, contract_id: str) -> ContractDocument:
        """Get contract by ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/contracts/{contract_id}",
                headers=self._headers
            )
            response.raise_for_status()
            return ContractDocument(**response.json())

    async def update_contract_state(
        self,
        contract_id: str,
        state: ContractState,
        error_message: Optional[str] = None
    ) -> bool:
        """Update contract state"""
        data = {"state": state.value}
        if error_message:
            data["error_message"] = error_message

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/v1/contracts/{contract_id}/state",
                json=data,
                headers=self._headers
            )
            response.raise_for_status()
            return True

    async def save_analysis_result(
        self,
        contract_id: str,
        analysis_result: ContractAnalysisResultDB
    ) -> bool:
        """Save contract analysis results"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/contracts/{contract_id}/analysis",
                json=analysis_result.model_dump(),
                headers=self._headers
            )
            response.raise_for_status()
            return True

    async def save_evaluation_result(
        self,
        contract_id: str,
        evaluation_result: ContractEvaluationResultDB
    ) -> bool:
        """Save contract evaluation results"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/contracts/{contract_id}/evaluation",
                json=evaluation_result.model_dump(),
                headers=self._headers
            )
            response.raise_for_status()
            return True