import time
import asyncio
from pathlib import Path
from typing import Dict, Any

from pwc.task_interface.base import ContractTaskExecutor
from pwc.task_interface.schema import ContractAnalysisResult, ExtractedClause, ClauseType
from pwc.ai import AIFactory
from pwc.storage import StorageFactory
from pwc.settings import settings


class AnalyzeContractExecutor(ContractTaskExecutor):
    """Executor for contract clause analysis"""

    async def run(self, task_info_dict: Dict[str, Any]) -> ContractAnalysisResult:
        """Analyze contract clauses using GenAI"""
        start_time = time.time()

        self.logger.info(f"Starting contract analysis for {self.task_info.contract_id}")

        try:
            # Get contract details from API
            contract = await self.api.get_contract(self.task_info.contract_id)

            # Initialize storage
            storage = StorageFactory.create_storage(
                settings.storage_type,
                base_path=settings.local_storage_path
            )

            # Read contract file
            file_content = await storage.load(contract["file_path"])

            # Initialize AI client (using existing GenAI factory)
            ai_client = AIFactory.create_client(
                settings.ai_provider,
                api_key=settings.openai_api_key,
                model=settings.openai_model
            )

            # Use the existing analyze_contract method from GenAI client
            analysis_result = await ai_client.analyze_contract(file_content)

            # Convert to our format
            clauses = [
                ExtractedClause(
                    type=ClauseType(clause.type) if hasattr(clause, 'type') else ClauseType.other,
                    content=clause.content if hasattr(clause, 'content') else str(clause),
                    confidence=getattr(clause, 'confidence', 0.8),
                    page_number=getattr(clause, 'page_number', None),
                    section=getattr(clause, 'section', None)
                )
                for clause in analysis_result.clauses
            ]

            # Create analysis result
            processing_time = time.time() - start_time
            result = ContractAnalysisResult(
                clauses=clauses,
                metadata={
                    "contract_id": self.task_info.contract_id,
                    "file_path": contract["file_path"],
                    "analysis_timestamp": time.time(),
                    "original_metadata": analysis_result.metadata
                },
                processing_time=processing_time,
                model_used=settings.openai_model
            )

            # Save result via API
            await self.api.save_analysis_result(self.task_info.contract_id, result)

            self.logger.info(f"Contract analysis completed in {processing_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Contract analysis failed: {e}")
            await self.api.report_failure(
                self.task_info.contract_id,
                f"Analysis failed: {str(e)}",
                "analysis_error"
            )
            raise

