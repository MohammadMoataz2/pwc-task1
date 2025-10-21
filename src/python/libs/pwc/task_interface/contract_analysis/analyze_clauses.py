from celery import Task
from pwc.task_interface.base import TaskInfo


class AnalyzeContractClausesTask(Task):
    """Shared task for contract clause analysis"""
    name = "contract_analysis.analyze_clauses"

    def run(self, task_info_dict: dict):
        """Entry point called by Celery - delegates to worker implementation"""
        # This will be implemented by the worker that registers this task
        # The worker will provide the actual implementation via task registry
        pass


# Create task instance that can be imported and used in workflows
analyze_contract_clauses = AnalyzeContractClausesTask()