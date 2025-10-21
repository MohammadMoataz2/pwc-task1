import time
import asyncio
from typing import Dict, Any

from pwc.task_interface.base import ContractTaskExecutor
from pwc.task_interface.schema import ContractEvaluationResult
from pwc.ai import AIFactory
from pwc.settings import settings


class EvaluateContractExecutor(ContractTaskExecutor):
    """Executor for contract health evaluation"""

    async def run(self, task_info_dict: Dict[str, Any]) -> ContractEvaluationResult:
        """Evaluate contract health and approval status"""
        start_time = time.time()

        self.logger.info(f"Starting contract evaluation for {self.task_info.contract_id}")

        try:
            # Get contract details and analysis result from API
            contract = await self.api.get_contract(self.task_info.contract_id)

            # Check if analysis result exists
            if not contract.get("analysis_result"):
                raise ValueError("Contract analysis must be completed before evaluation")

            analysis_result = contract["analysis_result"]

            # Initialize AI client (using existing GenAI factory)
            ai_client = AIFactory.create_client(
                settings.ai_provider,
                api_key=settings.openai_api_key,
                model=settings.openai_model
            )

            # Convert analysis result clauses to the format expected by evaluate_contract
            from pwc.ai.base import ContractClause
            clause_objects = []
            for clause_data in analysis_result.get("clauses", []):
                clause_obj = ContractClause(
                    type=clause_data.get("type", "other"),
                    content=clause_data.get("content", ""),
                    confidence=clause_data.get("confidence", 0.5)
                )
                clause_objects.append(clause_obj)

            # Use the existing evaluate_contract method from GenAI client
            evaluation_result = await ai_client.evaluate_contract(clause_objects)

            # Convert to our format
            evaluation = ContractEvaluationResult(
                approved=evaluation_result.approved,
                reasoning=evaluation_result.reasoning,
                risk_score=getattr(evaluation_result, 'risk_score', 0.5),
                recommendations=getattr(evaluation_result, 'recommendations', []),
                critical_issues=getattr(evaluation_result, 'critical_issues', []),
                processing_time=time.time() - start_time
            )

            # Save result via API
            await self.api.save_evaluation_result(self.task_info.contract_id, evaluation)

            processing_time = time.time() - start_time
            self.logger.info(f"Contract evaluation completed in {processing_time:.2f}s")
            return evaluation

        except Exception as e:
            self.logger.error(f"Contract evaluation failed: {e}")
            await self.api.report_failure(
                self.task_info.contract_id,
                f"Evaluation failed: {str(e)}",
                "evaluation_error"
            )
            raise

