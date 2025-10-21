from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
    celery: str


@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for liveness probe"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@router.get("/readyz", response_model=ReadinessResponse)
async def readiness_check():
    """Readiness check endpoint"""
    # TODO: Add actual database and celery health checks
    return ReadinessResponse(
        status="ready",
        database="connected",
        celery="available"
    )