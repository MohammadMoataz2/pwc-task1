"""
Task registry for mapping shared task interfaces to local implementations
Following the reference project pattern
"""
import logging
from typing import Dict, Type, Callable

from pwc.task_interface.base import TaskExecutor, TaskInfo
from pwc.logger import setup_logger

logger = setup_logger(__name__)


class TaskRegistry:
    """Registry for mapping task names to executor classes"""

    def __init__(self):
        self._tasks: Dict[str, Type[TaskExecutor]] = {}
        self._logger_factory: Callable = setup_logger

    def register_task(
        self,
        task_name: str,
        executor_class: Type[TaskExecutor],
        logger_factory: Callable = None
    ):
        """Register a task executor for a given task name"""
        self._tasks[task_name] = executor_class
        if logger_factory:
            self._logger_factory = logger_factory

        logger.info(f"Registered task: {task_name} -> {executor_class.__name__}")

    def get_executor(self, task_name: str, task_info: TaskInfo) -> TaskExecutor:
        """Get an executor instance for a task"""
        if task_name not in self._tasks:
            raise ValueError(f"Task {task_name} not registered")

        executor_class = self._tasks[task_name]
        task_logger = self._logger_factory()
        return executor_class(task_info, task_logger)

    def list_tasks(self) -> Dict[str, str]:
        """List all registered tasks"""
        return {name: executor.__name__ for name, executor in self._tasks.items()}


# Global task registry instance
task_registry = TaskRegistry()