from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ...core.security import get_current_user, TokenUser
from ...db.models import LogEntry

router = APIRouter()


class LogResponse(BaseModel):
    id: str
    timestamp: datetime
    user: Optional[str]
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    ip_address: Optional[str]


@router.get("/", response_model=List[LogResponse])
async def get_logs(
    skip: int = 0,
    limit: int = 100,
    user: Optional[str] = Query(None),
    endpoint: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    current_user: TokenUser = Depends(get_current_user)
):
    """Get paginated logs with optional filters"""
    query = {}
    if user:
        query["user"] = user
    if endpoint:
        query["endpoint"] = {"$regex": endpoint, "$options": "i"}
    if status:
        query["status_code"] = status

    logs = await LogEntry.find(query).skip(skip).limit(limit).sort("-timestamp").to_list()

    return [
        LogResponse(
            id=str(log.id),
            timestamp=log.timestamp,
            user=log.user,
            endpoint=log.endpoint,
            method=log.method,
            status_code=log.status_code,
            response_time_ms=log.response_time_ms,
            ip_address=log.ip_address
        )
        for log in logs
    ]