from typing import Dict, Any

from pwc.task_interface.base import ContractTaskExecutor


class ReportFailureExecutor(ContractTaskExecutor):
    """Executor for reporting contract processing failures"""

    async def run(self, error_message: str, task_info_dict: Dict[str, Any]) -> None:
        """Report contract processing failure via API"""
        self.logger.error(f"Reporting failure for contract {self.task_info.contract_id}: {error_message}")

        try:
            # Report failure via API
            await self.api.report_failure(
                self.task_info.contract_id,
                error_message,
                "task_failure"
            )

            self.logger.info(f"Successfully reported failure for contract {self.task_info.contract_id}")

        except Exception as e:
            self.logger.error(f"Failed to report failure: {e}")
            # Don't raise here as this is already an error handler