from typing import Dict, Any

from pwc.task_interface.base import ContractTaskExecutor
from pwc.task_interface.schema import ContractAnalysisResult, ExtractedClause, ClauseType
from pwc.factories import AnalyzeFactory
from pwc.storage import StorageFactory
from pwc.settings import settings


class AnalyzeContractExecutor(ContractTaskExecutor):
    """Executor for contract clause analysis using AI-based factory"""

    async def run(self, task_info_dict: Dict[str, Any]) -> ContractAnalysisResult:
        """Analyze contract clauses using AI factory"""
        self.logger.info(f"[EXECUTOR] Starting contract analysis for {self.task_info.contract_id}")

        try:
            # Initialize storage
            storage = StorageFactory.create_storage(
                settings.storage_type,
                base_path=settings.local_storage_path
            )

            # Load parsed text from previous parsing step
            text_file_path = f"parsed/{self.task_info.contract_id}/{self.task_info.run_id}/text.txt"
            self.logger.info(f"[EXECUTOR] Loading parsed text from: {text_file_path}")
            text_content = await storage.load(text_file_path)
            document_text = text_content.decode('utf-8')
            self.logger.info(f"[EXECUTOR] Loaded text: {len(document_text)} characters")

            # Analyze contract using factory
            analysis_result = await AnalyzeFactory.analyze(
                document_text,
                logger=self.logger
            )

            # Convert to our schema format
            clauses = [
                ExtractedClause(
                    type=ClauseType(clause.type) if clause.type in [e.value for e in ClauseType] else ClauseType.other,
                    content=clause.content,
                    confidence=clause.confidence,
                    page_number=getattr(clause, 'page_number', None),
                    section=getattr(clause, 'section', None)
                )
                for clause in analysis_result.clauses
            ]

            # Create final result
            result = ContractAnalysisResult(
                clauses=clauses,
                metadata={
                    "contract_id": self.task_info.contract_id,
                    "run_id": self.task_info.run_id,
                    "summary": getattr(analysis_result, 'summary', ''),
                    "ai_provider": settings.ai_provider,
                    "model_used": settings.openai_model
                },
                processing_time=0,  # TODO: Add timing
                model_used=settings.openai_model
            )

            # Save result via API
            await self.api.save_analysis_result(self.task_info.contract_id, result)

            self.logger.info(f"[EXECUTOR] Contract analysis completed for {self.task_info.contract_id}")
            self.logger.info(f"[EXECUTOR] Result: {len(result.clauses)} clauses extracted")
            return result

        except Exception as e:
            self.logger.error(f"Contract analysis failed: {e}")
            await self.api.report_failure(
                self.task_info.contract_id,
                f"Analysis failed: {str(e)}",
                "analysis_error"
            )
            raise

