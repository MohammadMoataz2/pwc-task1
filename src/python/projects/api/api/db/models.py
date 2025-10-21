from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from beanie import Document, PydanticObjectId
from pydantic import Field, BaseModel

from pwc.task_interface.schema import ContractState


class User(Document):
    """User model for authentication"""
    username: str = Field(..., unique=True)
    email: str = Field(..., unique=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"


class Client(Document):
    """Client model for contract organization"""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None
    company: Optional[str] = None
    created_by: str  # username
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "clients"


class Contract(Document):
    """Contract model - main entity for contract analysis"""
    filename: str
    file_path: str
    file_size: int
    content_type: str = "application/pdf"

    # Relationship
    client_id: Optional[PydanticObjectId] = None
    uploaded_by: str  # username

    # Contract details
    title: Optional[str] = None
    status: str = ContractState.pending.value

    # Analysis results (stored as dict to avoid schema dependencies)
    analysis_result: Optional[Dict[str, Any]] = None
    evaluation_result: Optional[Dict[str, Any]] = None

    # Pipeline tracking
    pipeline_runs: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None

    class Settings:
        name = "contracts"


class LogEntry(Document):
    """Log entry for API request tracking"""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Optional[str] = None
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    error_message: Optional[str] = None

    class Settings:
        name = "logs"


class MetricEntry(Document):
    """Metrics for system monitoring"""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metric_name: str
    metric_value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "metrics"