import sys
from pathlib import Path

# Add the shared library to the Python path
current_dir = Path(__file__).parent
libs_path = current_dir.parent.parent.parent.parent / "libs"
sys.path.insert(0, str(libs_path))

from celery import current_task
from pwc.settings import settings
from pwc.logger import setup_logger
from pwc.ai import AIFactory
from pwc.api_interface import APIClient
from pwc.task_interface import ContractState, ContractEvaluationResultDB
from pwc.ai.base import ContractClause
from ..main import celery_app
from ..core.database import worker_db

logger = setup_logger(__name__)

# Initialize AI client
ai_client = AIFactory.create_client(
    settings.ai_provider,
    api_key=settings.openai_api_key,
    model=settings.openai_model
)

# API client for callbacks
api_client = APIClient(base_url=settings.api_base_url)


@celery_app.task(bind=True)
def evaluate_contract(self, contract_id: str):
    """Evaluate contract health based on extracted clauses"""
    import asyncio
    return asyncio.run(_evaluate_contract_async(self, contract_id))


async def _evaluate_contract_async(task, contract_id: str):
    """Async implementation of contract evaluation"""
    try:
        logger.info(f"Starting contract evaluation for contract_id: {contract_id}")

        # Connect to database
        await worker_db.connect()

        # Update contract state to evaluating
        await api_client.update_contract_state(contract_id, ContractState.PROCESSING)

        # Get contract document from API
        contract = await api_client.get_contract(contract_id)

        # Check if analysis results exist
        if not contract.analysis_result or not contract.analysis_result.clauses:
            raise ValueError("No analysis results found for contract")

        # Convert database clauses to AI format
        clauses = [
            ContractClause(
                type=clause.type,
                content=clause.content,
                confidence=clause.confidence
            )
            for clause in contract.analysis_result.clauses
        ]

        # Evaluate contract using AI
        evaluation_result = await ai_client.evaluate_contract(clauses)

        # Convert to database format
        evaluation_result_db = ContractEvaluationResultDB(
            approved=evaluation_result.approved,
            reasoning=evaluation_result.reasoning,
            score=evaluation_result.score,
            model_used=settings.openai_model
        )

        # Save evaluation results to API
        await api_client.save_evaluation_result(contract_id, evaluation_result_db)

        # Update contract state to completed
        await api_client.update_contract_state(contract_id, ContractState.COMPLETED)

        # Send callback if configured
        if contract.callback_info:
            await _send_callback(contract_id, contract.callback_info)

        logger.info(f"Contract evaluation completed for contract_id: {contract_id}")

        return {
            "contract_id": contract_id,
            "status": "success",
            "approved": evaluation_result.approved,
            "score": evaluation_result.score
        }

    except Exception as e:
        logger.error(f"Contract evaluation failed for contract_id: {contract_id}, error: {str(e)}")

        # Update contract state to failed
        try:
            await api_client.update_contract_state(
                contract_id,
                ContractState.FAILED,
                error_message=str(e)
            )
        except Exception as callback_error:
            logger.error(f"Failed to update contract state: {callback_error}")

        # Re-raise the exception so Celery can handle retry logic
        raise

    finally:
        await worker_db.close()


async def _send_callback(contract_id: str, callback_info):
    """Send callback notification about completed contract analysis"""
    try:
        import httpx

        headers = callback_info.headers or {}
        if callback_info.auth_token:
            headers["Authorization"] = f"Bearer {callback_info.auth_token}"

        payload = {
            "contract_id": contract_id,
            "status": "completed",
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: Add proper timestamp
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=callback_info.method,
                url=callback_info.url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()

        logger.info(f"Callback sent successfully for contract_id: {contract_id}")

    except Exception as e:
        logger.error(f"Failed to send callback for contract_id: {contract_id}, error: {str(e)}")
        # Don't raise exception here as callback failure shouldn't fail the main task