from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from pydantic import BaseModel

from ...core.security import get_current_user
from ...db.models import Client, Contract

router = APIRouter()


class ClientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    company: Optional[str] = None


class ClientResponse(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    created_by: str
    created_at: datetime


class ContractSummary(BaseModel):
    id: str
    filename: str
    status: str
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


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    current_user: str = Depends(get_current_user)
):
    """Get all clients for the current user"""
    clients = await Client.find(Client.created_by == current_user).to_list()

    return [
        ClientResponse(
            id=str(client.id),
            name=client.name,
            email=client.email,
            company=client.company,
            created_by=client.created_by,
            created_at=client.created_at
        )
        for client in clients
    ]


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

    # Ensure user can only access their own clients
    if client.created_by != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this client"
        )

    contracts = await Contract.find(Contract.client_id == PydanticObjectId(client_id)).to_list()

    return [
        ContractSummary(
            id=str(contract.id),
            filename=contract.filename,
            status=contract.status,
            created_at=contract.created_at
        )
        for contract in contracts
    ]