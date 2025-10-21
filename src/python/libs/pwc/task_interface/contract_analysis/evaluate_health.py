from celery import Task
from pwc.task_interface.base import TaskInfo


class EvaluateContractHealthTask(Task):
    """Shared task for contract health evaluation"""
    name = "contract_analysis.evaluate_health"

    def run(self, task_info_dict: dict):
        """Entry point called by Celery - delegates to worker implementation"""
        # This will be implemented by the worker that registers this task
        # The worker will provide the actual implementation via task registry
        pass


# Create task instance that can be imported and used in workflows
evaluate_contract_health = EvaluateContractHealthTask()