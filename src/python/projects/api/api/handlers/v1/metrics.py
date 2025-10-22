from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from ...core.security import get_current_user, TokenUser
from ...db.models import LogEntry, Contract, Client

router = APIRouter()


class UserMetricsResponse(BaseModel):
    user_request_count: int
    user_avg_latency: float
    user_contract_count: int
    user_client_count: int
    user_processed_contracts: int
    user_failed_contracts: int
    top_endpoints: List[Dict[str, Any]]


class SystemMetricsResponse(BaseModel):
    total_request_count: int
    system_avg_latency: float
    total_contract_count: int
    total_client_count: int
    total_processed_contracts: int
    total_failed_contracts: int
    error_rate: float
    top_users: List[Dict[str, Any]]
    endpoint_stats: List[Dict[str, Any]]


@router.get("/user", response_model=UserMetricsResponse)
async def get_user_metrics(current_user: TokenUser = Depends(get_current_user)):
    """Get metrics for the current user"""
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    # User request metrics from logs
    user_logs = await LogEntry.find(
        LogEntry.user == current_user.username,
        LogEntry.timestamp >= last_24h
    ).to_list()

    user_request_count = len(user_logs)
    user_avg_latency = sum(log.response_time_ms for log in user_logs) / max(len(user_logs), 1)

    # User contract metrics
    user_contract_count = await Contract.find(Contract.uploaded_by == current_user.username).count()
    user_processed_contracts = await Contract.find(
        Contract.uploaded_by == current_user.username,
        Contract.status == "completed"
    ).count()
    user_failed_contracts = await Contract.find(
        Contract.uploaded_by == current_user.username,
        Contract.status == "failed"
    ).count()

    # User client count
    user_client_count = await Client.find(Client.created_by == current_user.username).count()

    # Top endpoints for user
    endpoint_counts = {}
    for log in user_logs:
        endpoint = log.endpoint
        if endpoint in endpoint_counts:
            endpoint_counts[endpoint] += 1
        else:
            endpoint_counts[endpoint] = 1

    top_endpoints = [
        {"endpoint": endpoint, "count": count}
        for endpoint, count in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    return UserMetricsResponse(
        user_request_count=user_request_count,
        user_avg_latency=user_avg_latency,
        user_contract_count=user_contract_count,
        user_client_count=user_client_count,
        user_processed_contracts=user_processed_contracts,
        user_failed_contracts=user_failed_contracts,
        top_endpoints=top_endpoints
    )


@router.get("/system", response_model=SystemMetricsResponse)
async def get_system_metrics(current_user: TokenUser = Depends(get_current_user)):
    """Get system-wide metrics (admin view)"""
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    # System request metrics from logs
    all_logs = await LogEntry.find(LogEntry.timestamp >= last_24h).to_list()
    total_request_count = len(all_logs)
    system_avg_latency = sum(log.response_time_ms for log in all_logs) / max(len(all_logs), 1)

    # Error rate
    error_logs = [log for log in all_logs if log.status_code >= 400]
    error_rate = len(error_logs) / max(len(all_logs), 1) * 100

    # System contract metrics
    total_contract_count = await Contract.count()
    total_client_count = await Client.count()
    total_processed_contracts = await Contract.find(Contract.status == "completed").count()
    total_failed_contracts = await Contract.find(Contract.status == "failed").count()

    # Top users by request count
    user_counts = {}
    for log in all_logs:
        if log.user:
            if log.user in user_counts:
                user_counts[log.user] += 1
            else:
                user_counts[log.user] = 1

    top_users = [
        {"user": user, "request_count": count}
        for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # Endpoint statistics
    endpoint_stats = {}
    for log in all_logs:
        endpoint = log.endpoint
        if endpoint not in endpoint_stats:
            endpoint_stats[endpoint] = {
                "count": 0,
                "total_latency": 0,
                "error_count": 0
            }

        endpoint_stats[endpoint]["count"] += 1
        endpoint_stats[endpoint]["total_latency"] += log.response_time_ms
        if log.status_code >= 400:
            endpoint_stats[endpoint]["error_count"] += 1

    endpoint_list = []
    for endpoint, stats in endpoint_stats.items():
        avg_latency = stats["total_latency"] / max(stats["count"], 1)
        error_rate = stats["error_count"] / max(stats["count"], 1) * 100

        endpoint_list.append({
            "endpoint": endpoint,
            "count": stats["count"],
            "avg_latency": round(avg_latency, 2),
            "error_rate": round(error_rate, 2)
        })

    endpoint_list.sort(key=lambda x: x["count"], reverse=True)

    return SystemMetricsResponse(
        total_request_count=total_request_count,
        system_avg_latency=round(system_avg_latency, 2),
        total_contract_count=total_contract_count,
        total_client_count=total_client_count,
        total_processed_contracts=total_processed_contracts,
        total_failed_contracts=total_failed_contracts,
        error_rate=round(error_rate, 2),
        top_users=top_users,
        endpoint_stats=endpoint_list[:10]
    )


# Backwards compatibility
@router.get("/", response_model=UserMetricsResponse)
async def get_metrics(current_user: TokenUser = Depends(get_current_user)):
    """Get user metrics (backwards compatible endpoint)"""
    return await get_user_metrics(current_user)