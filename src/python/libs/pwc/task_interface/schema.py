from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ContractState(str, Enum):
    """Contract processing states"""
    pending = "pending"
    processing = "processing"
    analyzing = "analyzing"
    evaluating = "evaluating"
    completed = "completed"
    failed = "failed"
    rejected = "rejected"


class ClauseType(str, Enum):
    """Types of contract clauses"""
    payment_terms = "payment_terms"
    termination = "termination"
    liability = "liability"
    confidentiality = "confidentiality"
    intellectual_property = "intellectual_property"
    governing_law = "governing_law"
    dispute_resolution = "dispute_resolution"
    force_majeure = "force_majeure"
    warranties = "warranties"
    indemnification = "indemnification"
    other = "other"


class ExtractedClause(BaseModel):
    """A single extracted clause from the contract"""
    type: ClauseType
    content: str
    confidence: float
    page_number: Optional[int] = None
    section: Optional[str] = None


class ContractAnalysisResult(BaseModel):
    """Result of contract clause analysis"""
    clauses: List[ExtractedClause]
    metadata: Dict[str, Any]
    processing_time: float
    model_used: str


class ContractEvaluationResult(BaseModel):
    """Result of contract health evaluation"""
    approved: bool
    reasoning: str
    risk_score: float
    recommendations: List[str]
    critical_issues: List[str]
    processing_time: float


class ContractProcessingStatus(BaseModel):
    """Overall contract processing status"""
    contract_id: str
    state: ContractState
    run_id: str
    analysis_result: Optional[ContractAnalysisResult] = None
    evaluation_result: Optional[ContractEvaluationResult] = None
    error_message: Optional[str] = None