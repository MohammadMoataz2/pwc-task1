from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
from typing import List
import PyPDF2
import io
import traceback

from ...core.security import get_current_user, TokenUser
from pwc.ai import AIFactory
from pwc.settings import settings
from pwc.storage import StorageFactory
from pwc.logger import setup_logger

router = APIRouter()

# Setup logger
logger = setup_logger(__name__)

# Initialize AI client
ai_client = AIFactory.create_client(
    settings.ai_provider,
    api_key=settings.openai_api_key,
    model=settings.openai_model
)

# Initialize storage
storage = StorageFactory.create_storage(
    settings.storage_type,
    base_path=settings.local_storage_path
)


class AnalysisResponse(BaseModel):
    clauses: list
    metadata: dict


class EvaluationResponse(BaseModel):
    approved: bool
    reasoning: str


class EvaluateClausesRequest(BaseModel):
    clauses: List[dict]


@router.post("/analyze-contract", response_model=AnalysisResponse)
async def analyze_contract(
    file: UploadFile = File(...),
    current_user: TokenUser = Depends(get_current_user)
):
    """Analyze contract PDF and extract clauses"""
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Read PDF content as bytes
    pdf_bytes = await file.read()

    try:
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        contract_text = ""
        for page in pdf_reader.pages:
            contract_text += page.extract_text() + "\n"

        if not contract_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from PDF. Please ensure the PDF contains readable text."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )

    # Now pass the extracted text to AI client
    result = await ai_client.analyze_contract(contract_text)

    return AnalysisResponse(
        clauses=[clause.model_dump() for clause in result.clauses],
        metadata=result.metadata
    )


@router.post("/evaluate-contract/{document_id}", response_model=EvaluationResponse)
async def evaluate_contract(
    document_id: str,
    current_user: TokenUser = Depends(get_current_user)
):
    """Evaluate contract health based on document's analysis results"""
    from ...db.models import Contract
    from pwc.ai.base import ContractClause

    # Get the contract document
    contract = await Contract.get(document_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check if contract has analysis results
    if not contract.analysis_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract must be analyzed first before evaluation"
        )

    # Extract clauses from analysis results
    analysis_clauses = contract.analysis_result.get("clauses", [])
    if not analysis_clauses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No clauses found in analysis results"
        )

    # Convert to ContractClause objects
    clause_objects = [ContractClause(**clause) for clause in analysis_clauses]

    # Evaluate contract
    result = await ai_client.evaluate_contract(clause_objects)

    # Store evaluation result in the contract
    contract.evaluation_result = {
        "approved": result.approved,
        "reasoning": result.reasoning,
        "score": result.score,
        "evaluated_at": datetime.now(datetime.timezone.utc).isoformat()
    }
    await contract.save()

    return EvaluationResponse(
        approved=result.approved,
        reasoning=result.reasoning
    )


@router.post("/analyze-document/{document_id}", response_model=AnalysisResponse)
async def analyze_document(
    document_id: str,
    current_user: TokenUser = Depends(get_current_user)
):
    """Analyze document by ID and save results to MongoDB"""
    try:
        logger.info(f"Starting document analysis for ID: {document_id}")
        from ...db.models import Contract

        # Get the contract document
        contract = await Contract.get(document_id)
        if not contract:
            logger.warning(f"Contract not found: {document_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )


        logger.info(f"Reading file from path: {contract.file_path}")

        # Read PDF from storage
        try:
            pdf_bytes = await storage.load(contract.file_path)
            logger.info(f"Successfully read {len(pdf_bytes)} bytes from storage")
        except Exception as e:
            logger.error(f"Error reading contract file: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading contract file: {str(e)}"
            )

        # Extract text from PDF
        try:
            logger.info("Extracting text from PDF")
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            contract_text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                contract_text += page_text + "\n"
                logger.debug(f"Extracted {len(page_text)} chars from page {i+1}")

            if not contract_text.strip():
                logger.warning("No text extracted from PDF")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from PDF. Please ensure the PDF contains readable text."
                )

            logger.info(f"Successfully extracted {len(contract_text)} characters from PDF")
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing PDF: {str(e)}"
            )

        # Analyze with AI
        try:
            logger.info("Starting AI analysis")
            result = await ai_client.analyze_contract(contract_text)
            logger.info(f"AI analysis completed with {len(result.clauses)} clauses")
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error in AI analysis: {str(e)}"
            )

        # Save analysis results to contract
        try:
            contract.analysis_result = {
                "clauses": [clause.model_dump() for clause in result.clauses],
                "metadata": result.metadata,
            }
            await contract.save()
            logger.info("Analysis results saved to database")
        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving analysis results: {str(e)}"
            )

        return AnalysisResponse(
            clauses=[clause.model_dump() for clause in result.clauses],
            metadata=result.metadata
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_document: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/evaluate-document/{document_id}", response_model=EvaluationResponse)
async def evaluate_document(
    document_id: str,
    current_user: TokenUser = Depends(get_current_user)
):
    """Evaluate document by ID and save results to MongoDB"""
    from ...db.models import Contract
    from pwc.ai.base import ContractClause

    # Get the contract document
    contract = await Contract.get(document_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )


    # Check if contract has analysis results
    if not contract.analysis_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract must be analyzed first before evaluation"
        )

    # Extract clauses from analysis results
    analysis_clauses = contract.analysis_result.get("clauses", [])
    if not analysis_clauses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No clauses found in analysis results"
        )

    # Convert to ContractClause objects
    clause_objects = [ContractClause(**clause) for clause in analysis_clauses]

    # Evaluate contract
    result = await ai_client.evaluate_contract(clause_objects)

    # Store evaluation result in the contract
    contract.evaluation_result = {
        "approved": result.approved,
        "reasoning": result.reasoning,
        "score": result.score,
    }
    await contract.save()

    return EvaluationResponse(
        approved=result.approved,
        reasoning=result.reasoning
    )


@router.post("/evaluate-clauses", response_model=EvaluationResponse)
async def evaluate_clauses(
    request: EvaluateClausesRequest,
    current_user: TokenUser = Depends(get_current_user)
):
    """Evaluate clauses directly without saving to database"""
    from pwc.ai.base import ContractClause

    if not request.clauses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No clauses provided for evaluation"
        )

    # Convert to ContractClause objects
    try:
        clause_objects = [ContractClause(**clause) for clause in request.clauses]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid clause format: {str(e)}"
        )

    # Evaluate clauses
    result = await ai_client.evaluate_contract(clause_objects)

    return EvaluationResponse(
        approved=result.approved,
        reasoning=result.reasoning
    )