from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Path, status, BackgroundTasks, Depends
from beanie import PydanticObjectId
from pydantic import BaseModel

from api.core.security import verify_internal_token
from api.db.models import Contract, User
from pwc.task_interface.schema import (
    ContractState,
    ContractAnalysisResult,
    ContractEvaluationResult
)

router = APIRouter()


class FailureRequest(BaseModel):
    error_message: str
    error_type: str = "processing_error"


async def _get_contract(contract_id: str) -> Contract:
    """Get contract by ID with error handling"""
    try:
        contract_obj_id = PydanticObjectId(contract_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid contract ID format")

    contract = await Contract.get(contract_obj_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/{contract_id}/internal")
async def get_contract_internal(
    contract_id: str = Path(..., description="Contract ID"),
    _: str = Depends(verify_internal_token)
):
    """Get contract details for internal worker access"""
    contract = await _get_contract(contract_id)
    return contract


@router.get("/{contract_id}/internal/pipeline/{run_id}/is-latest")
async def is_pipeline_latest(
    contract_id: str = Path(..., description="Contract ID"),
    run_id: str = Path(..., description="Pipeline run ID"),
    _: str = Depends(verify_internal_token)
):
    """Check if pipeline run is the latest for this contract"""
    contract = await _get_contract(contract_id)

    # Check if this run_id is the latest in pipeline_runs
    is_latest = (
        len(contract.pipeline_runs) > 0 and
        contract.pipeline_runs[-1].get("run_id") == run_id
    )

    return {"is_latest": is_latest}


@router.put("/{contract_id}/internal/change-state")
async def change_contract_state(
    state: str,
    contract_id: str = Path(..., description="Contract ID"),
    run_id: Optional[str] = None,
    _: str = Depends(verify_internal_token)
):
    """Update contract processing state"""
    contract = await _get_contract(contract_id)

    # Validate state
    try:
        new_state = ContractState(state)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid state: {state}")

    # Update state and timestamp
    contract.status = new_state.value
    contract.updated_at = datetime.now(timezone.utc)

    # Add pipeline run if provided
    if run_id:
        pipeline_run = {
            "run_id": run_id,
            "state": new_state.value,
            "timestamp": datetime.now(timezone.utc)
        }
        if not contract.pipeline_runs:
            contract.pipeline_runs = []
        contract.pipeline_runs.append(pipeline_run)

    await contract.save()
    return {"message": f"Contract state updated to {new_state.value}"}


@router.post("/{contract_id}/internal/set-analysis-result")
async def set_analysis_result(
    analysis_result: ContractAnalysisResult,
    contract_id: str = Path(..., description="Contract ID"),
    _: str = Depends(verify_internal_token)
):
    """Save contract clause analysis result"""
    contract = await _get_contract(contract_id)

    # Update contract with analysis results
    contract.analysis_result = analysis_result.dict()
    contract.updated_at = datetime.now(timezone.utc)

    await contract.save()
    return {"message": "Analysis result saved successfully"}


@router.post("/{contract_id}/internal/set-evaluation-result")
async def set_evaluation_result(
    evaluation_result: ContractEvaluationResult,
    contract_id: str = Path(..., description="Contract ID"),
    _: str = Depends(verify_internal_token)
):
    """Save contract health evaluation result"""
    contract = await _get_contract(contract_id)

    # Update contract with evaluation results
    contract.evaluation_result = evaluation_result.dict()
    contract.updated_at = datetime.now(timezone.utc)

    await contract.save()
    return {"message": "Evaluation result saved successfully"}


@router.put("/{contract_id}/internal/failed")
async def report_contract_failure(
    failure_data: FailureRequest,
    contract_id: str = Path(..., description="Contract ID"),
    _: str = Depends(verify_internal_token)
):
    """Report contract processing failure"""
    contract = await _get_contract(contract_id)

    # Update contract with failure information
    contract.status = ContractState.failed.value
    contract.error_message = failure_data.error_message
    # contract.error_type = failure_data.error_type
    contract.updated_at = datetime.now(timezone.utc)

    await contract.save()
    return {"message": "Contract failure reported"}


@router.get("/{contract_id}/internal/status")
async def get_contract_status(
    contract_id: str = Path(..., description="Contract ID"),
    _: str = Depends(verify_internal_token)
):
    """Get detailed contract processing status"""
    contract = await _get_contract(contract_id)

    return {
        "contract_id": str(contract.id),
        "state": contract.status,
        "pipeline_runs": contract.pipeline_runs or [],
        "analysis_result": contract.analysis_result,
        "evaluation_result": contract.evaluation_result,
        "error_message": getattr(contract, 'error_message', None),
        "updated_at": contract.updated_at
    }