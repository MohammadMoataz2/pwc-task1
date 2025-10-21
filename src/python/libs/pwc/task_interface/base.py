from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod
import logging

from pwc.api_interface import APIClient


@dataclass
class TaskInfo:
    """Task execution context shared across all tasks"""
    run_id: str
    contract_id: str
    storage_root_path: Path
    api_auth_token: str
    api_base_url: str


class TaskExecutor(ABC):
    """Base class for all task executors"""

    def __init__(self, task_info: TaskInfo, logger: Optional[logging.Logger] = None):
        self.task_info = task_info
        self.logger = logger or logging.getLogger(__name__)

    @abstractmethod
    async def run(self, *args, **kwargs):
        """Execute the task logic"""
        pass

    async def start(self, *args, **kwargs):
        """Start task execution with error handling"""
        try:
            result = await self.run(*args, **kwargs)
            return await self.end(result)
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            raise

    async def end(self, result):
        """Finalize task execution"""
        return result


class ContractTaskExecutor(TaskExecutor):
    """Base class for contract-specific task executors"""

    def __init__(self, task_info: TaskInfo, logger: Optional[logging.Logger] = None):
        super().__init__(task_info, logger)
        self.api = APIClient(
            base_url=task_info.api_base_url,
            auth_token=task_info.api_auth_token,
            logger=self.logger
        )

    async def start(self, *args, **kwargs):
        """Verify pipeline is latest before execution"""
        if not await self.api.is_pipeline_latest(self.task_info.contract_id, self.task_info.run_id):
            self.logger.warning(f"Pipeline {self.task_info.run_id} is not latest for contract {self.task_info.contract_id}. Skipping.")
            return None

        return await super().start(*args, **kwargs)