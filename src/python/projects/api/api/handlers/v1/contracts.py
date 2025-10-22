from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from beanie import PydanticObjectId
from pydantic import BaseModel

from ...core.security import get_current_user, TokenUser
from ...db.models import Contract, Client
from pwc.task_interface.schema import ContractState
from pwc.storage import StorageFactory
from pwc.settings import settings
from ...core.celery_app import celery_app
from ...core.security import generate_internal_token

router = APIRouter()

# Initialize storage
storage = StorageFactory.create_storage(
    settings.storage_type,
    base_path=settings.local_storage_path
)


class ContractCreate(BaseModel):
    filename: str
    client_id: Optional[str] = None


class ContractResponse(BaseModel):
    id: str
    filename: str
    title: Optional[str] = None
    status: str
    client_id: Optional[str] = None
    uploaded_by: str
    created_at: datetime
    analysis_result: Optional[dict] = None
    evaluation_result: Optional[dict] = None


class ContractStateUpdate(BaseModel):
    status: str
    error_message: Optional[str] = None


@router.post("/", response_model=ContractResponse)
async def create_contract(
    file: UploadFile = File(...),
    client_id: Optional[str] = Form(None),
    current_user: TokenUser = Depends(get_current_user)
):
    """Upload and create a new contract"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )

    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Validate client exists if provided
    if client_id:
        client = await Client.get(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

    # Read file content
    content = await file.read()

    # Store file
    file_path = f"contracts/{datetime.now(timezone.utc).strftime('%Y/%m/%d')}/{file.filename}"
    stored_path = await storage.save(content, file_path)

    # Create contract record
    contract = Contract(
        filename=file.filename,
        title=file.filename,  # Use filename as title initially
        file_path=stored_path,
        file_size=len(content),
        content_type=file.content_type,
        client_id=PydanticObjectId(client_id) if client_id else None,
        uploaded_by=current_user.username
    )

    await contract.insert()

    return ContractResponse(
        id=str(contract.id),
        filename=contract.filename,
        title=contract.title,
        status=contract.status,
        client_id=str(contract.client_id) if contract.client_id else None,
        uploaded_by=contract.uploaded_by,
        created_at=contract.created_at,
        analysis_result=contract.analysis_result,
        evaluation_result=contract.evaluation_result
    )


@router.get("/", response_model=List[ContractResponse])
async def list_contracts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: TokenUser = Depends(get_current_user)
):
    """List contracts with optional filtering"""
    query = {"uploaded_by": current_user.username}  # Only show user's own contracts
    if status:
        query["status"] = status

    contracts = await Contract.find(query).skip(skip).limit(limit).to_list()

    return [
        ContractResponse(
            id=str(contract.id),
            filename=contract.filename,
            title=contract.title,
            status=contract.status,
            client_id=str(contract.client_id) if contract.client_id else None,
            uploaded_by=contract.uploaded_by,
            created_at=contract.created_at,
            analysis_result=contract.analysis_result,
            evaluation_result=contract.evaluation_result
        )
        for contract in contracts
    ]


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: str,
    current_user: TokenUser = Depends(get_current_user)
):
    """Get a specific contract"""
    contract = await Contract.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Ensure user can only access their own contracts
    if contract.uploaded_by != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this contract"
        )

    return ContractResponse(
        id=str(contract.id),
        filename=contract.filename,
        title=contract.title,
        status=contract.status,
        client_id=str(contract.client_id) if contract.client_id else None,
        uploaded_by=contract.uploaded_by,
        created_at=contract.created_at,
        analysis_result=contract.analysis_result,
        evaluation_result=contract.evaluation_result
    )


@router.patch("/{contract_id}/state")
async def update_contract_state(
    contract_id: str,
    state_update: ContractStateUpdate,
    current_user: TokenUser = Depends(get_current_user)
):
    """Update contract state (used by workers)"""
    contract = await Contract.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    contract.status = state_update.status
    contract.updated_at = datetime.now(timezone.utc)
    if state_update.error_message:
        contract.error_message = state_update.error_message

    await contract.save()
    return {"message": "Contract state updated"}


@router.post("/{contract_id}/analysis")
async def save_analysis_result(
    contract_id: str,
    analysis_result: dict,
    current_user: TokenUser = Depends(get_current_user)
):
    """Save contract analysis results"""
    contract = await Contract.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    contract.analysis_result = analysis_result
    contract.status = ContractState.analyzing.value
    contract.updated_at = datetime.now(timezone.utc)
    await contract.save()

    return {"message": "Analysis result saved"}


@router.post("/{contract_id}/evaluation")
async def save_evaluation_result(
    contract_id: str,
    evaluation_result: dict,
    current_user: TokenUser = Depends(get_current_user)
):
    """Save contract evaluation results"""
    contract = await Contract.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    contract.evaluation_result = evaluation_result
    contract.status = ContractState.evaluating.value
    contract.updated_at = datetime.now(timezone.utc)
    await contract.save()

    return {"message": "Evaluation result saved"}


@router.post("/{contract_id}/init-genai")
async def trigger_genai_analysis(
    contract_id: str,
    current_user: TokenUser = Depends(get_current_user)
):
    """Trigger GenAI analysis pipeline for a contract"""
    contract = await Contract.get(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Allow analysis for pending, failed, and completed contracts
    allowed_states = [
        ContractState.pending.value,
        ContractState.failed.value,
        ContractState.completed.value
    ]

    if contract.status not in allowed_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract is not in a state that allows analysis. Current state: {contract.status}. Allowed states: {allowed_states}"
        )

    # Generate internal token for worker communication
    internal_token = generate_internal_token()

    # Create analysis workflow chain
    from uuid import uuid4
    from celery import chain

    # Generate run ID
    run_id = str(uuid4())

    # Create task info for the worker
    task_info_dict = {
        "run_id": run_id,
        "contract_id": str(contract.id),
        "storage_root_path": str(settings.local_storage_path + "/contracts/" + str(contract.id) + "/" + run_id),
        "api_auth_token": internal_token,
        "api_base_url": settings.api_base_url
    }

    # Add pipeline run to contract
    pipeline_run = {
        "run_id": run_id,
        "state": ContractState.processing.value,
        "timestamp": datetime.now(timezone.utc)
    }
    contract.pipeline_runs.append(pipeline_run)
    contract.status = ContractState.processing.value
    contract.updated_at = datetime.now(timezone.utc)
    await contract.save()

    # Create and execute the analysis pipeline using immutable signatures
    # This prevents tasks from receiving previous task results as arguments
    # NEW: Added separate parse step for strategy pattern
    pipeline = chain(
        celery_app.signature("contract_analysis.change_state", args=[ContractState.processing.value, task_info_dict], immutable=True),
        celery_app.signature("contract_analysis.parse_document", args=[task_info_dict], immutable=True),
        celery_app.signature("contract_analysis.analyze_clauses", args=[task_info_dict], immutable=True),
        celery_app.signature("contract_analysis.evaluate_health", args=[task_info_dict], immutable=True),
        celery_app.signature("contract_analysis.change_state", args=[ContractState.completed.value, task_info_dict], immutable=True)
    )

    # Execute the pipeline asynchronously
    async_result = pipeline.apply_async()

    return {
        "message": "Analysis pipeline triggered",
        "task_id": async_result.id if hasattr(async_result, 'id') else str(async_result),
        "run_id": run_id,
        "contract_id": contract_id
    }