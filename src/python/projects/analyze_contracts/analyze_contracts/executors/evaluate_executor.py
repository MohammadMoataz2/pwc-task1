from typing import Dict, Any

from pwc.task_interface.base import ContractTaskExecutor
from pwc.task_interface.schema import ContractEvaluationResult
from pwc.factories import EvaluateFactory
from pwc.ai.base import ContractClause
from pwc.settings import settings


class EvaluateContractExecutor(ContractTaskExecutor):
    """Executor for contract health evaluation using AI-based factory"""

    async def run(self, task_info_dict: Dict[str, Any]) -> ContractEvaluationResult:
        """Evaluate contract health using AI factory"""
        self.logger.info(f"[EXECUTOR] Starting contract evaluation for {self.task_info.contract_id}")

        try:
            # Get contract with analysis results from API
            self.logger.info(f"[EXECUTOR] Fetching contract with analysis results from API")
            contract = await self.api.get_contract(self.task_info.contract_id)
            self.logger.info(f"[EXECUTOR] Contract loaded with analysis results")

            # Extract clauses from analysis results
            if not contract.get("analysis_result") or not contract["analysis_result"].get("clauses"):
                self.logger.error(f"[EXECUTOR] No analysis results found for contract {self.task_info.contract_id}")
                raise ValueError("No analysis results found. Contract must be analyzed first.")

            self.logger.info(f"[EXECUTOR] Found {len(contract['analysis_result']['clauses'])} clauses to evaluate")

            # Convert to AI client format (ContractClause objects)
            clauses = [
                ContractClause(
                    type=clause.get("type", "unknown"),
                    content=clause.get("content", ""),
                    confidence=clause.get("confidence", 0.8)
                )
                for clause in contract["analysis_result"]["clauses"]
            ]

            # Evaluate contract using factory
            evaluation_result = await EvaluateFactory.evaluate(
                clauses,
                logger=self.logger
            )

            # Create final result
            result = ContractEvaluationResult(
                approved=evaluation_result.approved,
                risk_score=getattr(evaluation_result, 'score', 0.0),
                reasoning=evaluation_result.reasoning,
                recommendations=getattr(evaluation_result, 'recommendations', []),
                critical_issues=getattr(evaluation_result, 'critical_issues', []),
                processing_time=0  # TODO: Add timing
            )

            # Save result via API
            await self.api.save_evaluation_result(self.task_info.contract_id, result)

            self.logger.info(f"[EXECUTOR] Contract evaluation completed for {self.task_info.contract_id}")
            self.logger.info(f"[EXECUTOR] Result: approved={result.approved}, risk_score={result.risk_score}")
            return result

        except Exception as e:
            self.logger.error(f"Contract evaluation failed: {e}")
            await self.api.report_failure(
                self.task_info.contract_id,
                f"Evaluation failed: {str(e)}",
                "evaluation_error"
            )
            raise

