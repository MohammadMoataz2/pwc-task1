from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...core.security import get_current_user
from ...db.models import LogEntry, Contract

router = APIRouter()


class MetricsResponse(BaseModel):
    request_count: int
    avg_latency: float
    contract_count: int
    processed_contracts: int
    failed_contracts: int


@router.get("/", response_model=MetricsResponse)
async def get_metrics(current_user: str = Depends(get_current_user)):
    """Get system metrics"""
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    # Request metrics from logs
    recent_logs = await LogEntry.find(LogEntry.timestamp >= last_24h).to_list()
    request_count = len(recent_logs)
    avg_latency = sum(log.response_time_ms for log in recent_logs) / max(len(recent_logs), 1)

    # Contract metrics
    total_contracts = await Contract.count()
    processed_contracts = await Contract.find(Contract.state == "completed").count()
    failed_contracts = await Contract.find(Contract.state == "failed").count()

    return MetricsResponse(
        request_count=request_count,
        avg_latency=avg_latency,
        contract_count=total_contracts,
        processed_contracts=processed_contracts,
        failed_contracts=failed_contracts
    )