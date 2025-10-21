import sys
from pathlib import Path

# Add the shared library to the Python path
current_dir = Path(__file__).parent
libs_path = current_dir.parent.parent.parent.parent / "libs"
sys.path.insert(0, str(libs_path))

from celery import current_task
from pwc.settings import settings
from pwc.logger import setup_logger
from pwc.storage import StorageFactory
from pwc.ai import AIFactory
from pwc.api_interface import APIClient
from pwc.task_interface import ContractState, ContractAnalysisResultDB, ContractClauseDB
from ..main import celery_app
from ..core.database import worker_db

logger = setup_logger(__name__)

# Initialize storage and AI client
storage = StorageFactory.create_storage(
    settings.storage_type,
    base_path=settings.local_storage_path
)

ai_client = AIFactory.create_client(
    settings.ai_provider,
    api_key=settings.openai_api_key,
    model=settings.openai_model
)

# API client for callbacks
api_client = APIClient(base_url=settings.api_base_url)


@celery_app.task(bind=True)
def analyze_contract(self, contract_id: str):
    """Analyze contract and extract clauses using AI"""
    import asyncio
    return asyncio.run(_analyze_contract_async(self, contract_id))


async def _analyze_contract_async(task, contract_id: str):
    """Async implementation of contract analysis"""
    try:
        logger.info(f"Starting contract analysis for contract_id: {contract_id}")

        # Connect to database
        await worker_db.connect()

        # Update contract state to processing
        await api_client.update_contract_state(contract_id, ContractState.PROCESSING)

        # Get contract document from API
        contract = await api_client.get_contract(contract_id)

        # Load PDF content from storage
        pdf_content = await storage.load(contract.file_path)

        # Analyze contract using AI
        analysis_result = await ai_client.analyze_contract(pdf_content)

        # Convert to database format
        clauses_db = [
            ContractClauseDB(
                type=clause.type,
                content=clause.content,
                confidence=clause.confidence
            )
            for clause in analysis_result.clauses
        ]

        analysis_result_db = ContractAnalysisResultDB(
            clauses=clauses_db,
            metadata=analysis_result.metadata,
            model_used=settings.openai_model
        )

        # Save analysis results to API
        await api_client.save_analysis_result(contract_id, analysis_result_db)

        # Update contract state
        await api_client.update_contract_state(contract_id, ContractState.ANALYZED)

        # Trigger evaluation task
        celery_app.send_task(
            "analyze_contracts.tasks.evaluate.evaluate_contract",
            args=[contract_id]
        )

        logger.info(f"Contract analysis completed for contract_id: {contract_id}")

        return {
            "contract_id": contract_id,
            "status": "success",
            "clauses_count": len(analysis_result.clauses)
        }

    except Exception as e:
        logger.error(f"Contract analysis failed for contract_id: {contract_id}, error: {str(e)}")

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