import sys
import os
from pathlib import Path

# Add the shared library to the Python path
current_dir = Path(__file__).parent
libs_path = current_dir.parent.parent.parent / "libs"
sys.path.insert(0, str(libs_path))

from celery import Celery
from pwc.settings import settings
from pwc.logger import setup_logger
from pwc.task_interface.base import TaskInfo

# Import task registry and executors
from .task_registry import task_registry
from .executors import (
    AnalyzeContractExecutor,
    EvaluateContractExecutor,
    ChangeStateExecutor,
    ReportFailureExecutor
)

logger = setup_logger(__name__)

# Create Celery app
celery_app = Celery(
    "pwc_contract_analysis_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)


# Register task executors with the task registry
def register_tasks():
    """Register task executors following the reference project pattern"""
    task_registry.register_task(
        "contract_analysis.analyze_clauses",
        AnalyzeContractExecutor,
        logger_factory=lambda: setup_logger()
    )
    task_registry.register_task(
        "contract_analysis.evaluate_health",
        EvaluateContractExecutor,
        logger_factory=lambda: setup_logger()
    )
    task_registry.register_task(
        "contract_analysis.change_state",
        ChangeStateExecutor,
        logger_factory=lambda: setup_logger()
    )
    task_registry.register_task(
        "contract_analysis.report_failure",
        ReportFailureExecutor,
        logger_factory=lambda: setup_logger()
    )

    logger.info("Task executors registered successfully")


# Register shared task implementations
@celery_app.task(name="contract_analysis.analyze_clauses", bind=True)
def analyze_contract_clauses(self, task_info_dict):
    """Shared task: Analyze contract clauses"""
    task_info = TaskInfo(**task_info_dict)
    executor = task_registry.get_executor("contract_analysis.analyze_clauses", task_info)

    # Run the executor asynchronously
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(executor.run(task_info_dict))
        return result.dict() if hasattr(result, 'dict') else result
    finally:
        loop.close()


@celery_app.task(name="contract_analysis.evaluate_health", bind=True)
def evaluate_contract_health(self, task_info_dict):
    """Shared task: Evaluate contract health"""
    task_info = TaskInfo(**task_info_dict)
    executor = task_registry.get_executor("contract_analysis.evaluate_health", task_info)

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(executor.run(task_info_dict))
        return result.dict() if hasattr(result, 'dict') else result
    finally:
        loop.close()


@celery_app.task(name="contract_analysis.change_state", bind=True)
def change_contract_state(self, state, task_info_dict):
    """Shared task: Change contract state"""
    task_info = TaskInfo(**task_info_dict)
    executor = task_registry.get_executor("contract_analysis.change_state", task_info)

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(executor.run(state, task_info_dict))
        return result
    finally:
        loop.close()


@celery_app.task(name="contract_analysis.report_failure", bind=True)
def report_contract_failure(self, error_message, task_info_dict):
    """Shared task: Report contract failure"""
    task_info = TaskInfo(**task_info_dict)
    executor = task_registry.get_executor("contract_analysis.report_failure", task_info)

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(executor.run(error_message, task_info_dict))
        return result
    finally:
        loop.close()


# Register tasks on import
register_tasks()

if __name__ == "__main__":
    celery_app.start()