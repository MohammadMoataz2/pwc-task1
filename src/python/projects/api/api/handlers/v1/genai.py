from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel

from ...core.security import get_current_user
from pwc.ai import AIFactory
from pwc.settings import settings

router = APIRouter()

# Initialize AI client
ai_client = AIFactory.create_client(
    settings.ai_provider,
    api_key=settings.openai_api_key,
    model=settings.openai_model
)


class AnalysisResponse(BaseModel):
    clauses: list
    metadata: dict


class EvaluationResponse(BaseModel):
    approved: bool
    reasoning: str


@router.post("/analyze-contract", response_model=AnalysisResponse)
async def analyze_contract(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Analyze contract PDF and extract clauses"""
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    content = await file.read()
    result = await ai_client.analyze_contract(content)

    return AnalysisResponse(
        clauses=[clause.model_dump() for clause in result.clauses],
        metadata=result.metadata
    )


@router.post("/evaluate-contract", response_model=EvaluationResponse)
async def evaluate_contract(
    clauses: list,
    current_user: str = Depends(get_current_user)
):
    """Evaluate contract health based on clauses"""
    # Convert dict clauses back to ContractClause objects
    from pwc.ai.base import ContractClause
    clause_objects = [ContractClause(**clause) for clause in clauses]

    result = await ai_client.evaluate_contract(clause_objects)

    return EvaluationResponse(
        approved=result.approved,
        reasoning=result.reasoning
    )