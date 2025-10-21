from typing import Dict, Any

from pwc.task_interface.base import ContractTaskExecutor
from pwc.task_interface.schema import ContractState


class ChangeStateExecutor(ContractTaskExecutor):
    """Executor for changing contract state"""

    async def run(self, state: str, task_info_dict: Dict[str, Any]) -> None:
        """Change contract state via API"""
        self.logger.info(f"Changing contract {self.task_info.contract_id} state to {state}")

        try:
            # Validate state
            contract_state = ContractState(state)

            # Update state via API
            await self.api.update_contract_state(
                self.task_info.contract_id,
                contract_state,
                self.task_info.run_id
            )

            self.logger.info(f"Successfully changed contract state to {state}")

        except Exception as e:
            self.logger.error(f"Failed to change contract state: {e}")
            await self.api.report_failure(
                self.task_info.contract_id,
                f"State change failed: {str(e)}",
                "state_change_error"
            )
            raise