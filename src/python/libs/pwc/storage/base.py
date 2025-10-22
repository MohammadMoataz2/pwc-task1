from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path


class StorageInterface(ABC):
    """Abstract base class for storage implementations"""

    @abstractmethod
    async def save(self, content: bytes, file_path: str) -> str:
        """Save content to storage and return the stored path"""
        pass

    @abstractmethod
    async def load(self, file_path: str) -> bytes:
        """Load content from storage"""
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """Delete file from storage"""
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """Check if file exists in storage"""
        pass

    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """Get URL/path for accessing the file"""
        pass