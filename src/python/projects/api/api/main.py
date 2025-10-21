import sys
import os
from pathlib import Path

# Add the shared library to the Python path
current_dir = Path(__file__).parent
libs_path = current_dir.parent.parent.parent / "libs"
sys.path.insert(0, str(libs_path))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager

from pwc.settings import settings
from pwc.logger import setup_logger
from .core.database import init_database, close_database
from .core.celery_app import celery_app
from .handlers.v1 import auth, contracts, clients, genai, logs, metrics, health, internal_contracts
from .middleware import LoggingMiddleware

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting PWC Contract Analysis API")
    await init_database()
    app.celery_app = celery_app
    yield
    # Shutdown
    logger.info("Shutting down PWC Contract Analysis API")
    await close_database()


app = FastAPI(
    title="PWC Contract Analysis API",
    description="API for analyzing contracts using GenAI",
    version=settings.app_version,
    lifespan=lifespan
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# CORS
if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])
app.include_router(contracts.router, prefix=f"{settings.api_v1_prefix}/contracts", tags=["Contracts"])
app.include_router(clients.router, prefix=f"{settings.api_v1_prefix}/clients", tags=["Clients"])
app.include_router(genai.router, prefix=f"{settings.api_v1_prefix}/genai", tags=["GenAI"])
app.include_router(logs.router, prefix=f"{settings.api_v1_prefix}/logs", tags=["Logs"])
app.include_router(metrics.router, prefix=f"{settings.api_v1_prefix}/metrics", tags=["Metrics"])
app.include_router(health.router, tags=["Health"])
app.include_router(internal_contracts.router, prefix=f"{settings.api_v1_prefix}/contracts", tags=["Internal"])


@app.get("/")
async def root():
    return {
        "message": "PWC Contract Analysis API",
        "version": settings.app_version,
        "status": "operational"
    }