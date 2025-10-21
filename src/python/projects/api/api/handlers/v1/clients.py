from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from pydantic import BaseModel

from ...core.security import get_current_user
from ...db.models import Client, Contract

router = APIRouter()


class ClientCreate(BaseModel):
    name: str
    email: str = None
    company: str = None


class ClientResponse(BaseModel):
    id: str
    name: str
    email: str = None
    company: str = None
    created_by: str
    created_at: datetime


class ContractSummary(BaseModel):
    id: str
    filename: str
    state: str
    created_at: datetime


@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new client"""
    client = Client(
        name=client_data.name,
        email=client_data.email,
        company=client_data.company,
        created_by=current_user
    )
    await client.insert()

    return ClientResponse(
        id=str(client.id),
        name=client.name,
        email=client.email,
        company=client.company,
        created_by=client.created_by,
        created_at=client.created_at
    )


@router.get("/{client_id}/contracts", response_model=List[ContractSummary])
async def get_client_contracts(
    client_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get all contracts for a specific client"""
    client = await Client.get(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    contracts = await Contract.find(Contract.client_id == PydanticObjectId(client_id)).to_list()

    return [
        ContractSummary(
            id=str(contract.id),
            filename=contract.filename,
            state=contract.state.value,
            created_at=contract.created_at
        )
        for contract in contracts
    ]