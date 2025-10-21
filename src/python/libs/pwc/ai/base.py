from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel


class ParsedDocument(BaseModel):
    text: str
    page_count: int = 0
    metadata: Dict[str, Any] = {}


class ContractClause(BaseModel):
    type: str
    content: str
    confidence: float = 1.0


class ContractAnalysisResult(BaseModel):
    clauses: List[ContractClause]
    metadata: Dict[str, Any] = {}


class ContractEvaluationResult(BaseModel):
    approved: bool
    reasoning: str
    score: float = 0.0


class AIInterface(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    async def analyze_contract(self, pdf_content: bytes) -> ContractAnalysisResult:
        """Analyze contract PDF and extract clauses"""
        pass

    @abstractmethod
    async def evaluate_contract(self, clauses: List[ContractClause]) -> ContractEvaluationResult:
        """Evaluate contract health based on clauses"""
        pass