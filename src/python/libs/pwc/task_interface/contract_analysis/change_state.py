from celery import Task
from pwc.task_interface.base import TaskInfo
from pwc.task_interface.schema import ContractState


class ChangeContractStateTask(Task):
    """Shared task for updating contract state"""
    name = "contract_analysis.change_state"

    def run(self, state: str, task_info_dict: dict):
        """Entry point called by Celery - delegates to worker implementation"""
        # This will be implemented by the worker that registers this task
        # The worker will provide the actual implementation via task registry
        pass


# Create task instance that can be imported and used in workflows
change_contract_state = ChangeContractStateTask()