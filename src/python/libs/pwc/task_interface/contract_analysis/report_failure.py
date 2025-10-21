from celery import Task
from pwc.task_interface.base import TaskInfo


class ReportContractFailureTask(Task):
    """Shared task for reporting contract processing failures"""
    name = "contract_analysis.report_failure"

    def run(self, error_message: str, task_info_dict: dict):
        """Entry point called by Celery - delegates to worker implementation"""
        # This will be implemented by the worker that registers this task
        # The worker will provide the actual implementation via task registry
        pass


# Create task instance that can be imported and used in workflows
report_contract_failure = ReportContractFailureTask()