from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class ContractState(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    EVALUATED = "evaluated"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TaskStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class ContractType(str, Enum):
    SERVICE_AGREEMENT = "service_agreement"
    NDA = "nda"
    EMPLOYMENT = "employment"
    PURCHASE = "purchase"
    LEASE = "lease"
    UNKNOWN = "unknown"


class TaskInfo(BaseModel):
    task_id: str
    contract_id: str
    task_name: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContractMetadata(BaseModel):
    filename: str
    content_type: str = "application/pdf"
    file_size: int
    uploaded_by: str
    contract_type: ContractType = ContractType.UNKNOWN


class CallbackInfo(BaseModel):
    url: str
    method: str = "POST"
    headers: Dict[str, str] = Field(default_factory=dict)
    auth_token: Optional[str] = None


class ContractClauseDB(BaseModel):
    type: str
    content: str
    confidence: float = 1.0
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class ContractAnalysisResultDB(BaseModel):
    clauses: List[ContractClauseDB] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = "gpt-4"


class ContractEvaluationResultDB(BaseModel):
    approved: bool
    reasoning: str
    score: float = 0.0
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = "gpt-4"


class ContractDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    filename: str
    file_path: str
    metadata: ContractMetadata
    state: ContractState = ContractState.UPLOADED
    analysis_result: Optional[ContractAnalysisResultDB] = None
    evaluation_result: Optional[ContractEvaluationResultDB] = None
    callback_info: Optional[CallbackInfo] = None
    tasks: List[TaskInfo] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}