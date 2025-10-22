import os
import aiofiles
from pathlib import Path
from typing import Optional

from .base import StorageInterface


class LocalStorage(StorageInterface):
    """Local filesystem storage implementation"""

    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, file_path: str) -> Path:
        """Get full path for a file"""
        return self.base_path / file_path.lstrip("/")

    async def save(self, content: bytes, file_path: str) -> str:
        """Save content to local filesystem"""
        full_path = self._get_full_path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)

        return str(full_path.relative_to(self.base_path))

    async def load(self, file_path: str) -> bytes:
        """Load content from local filesystem"""
        full_path = self._get_full_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete(self, file_path: str) -> bool:
        """Delete file from local filesystem"""
        full_path = self._get_full_path(file_path)

        if full_path.exists():
            full_path.unlink()
            return True
        return False

    async def exists(self, file_path: str) -> bool:
        """Check if file exists"""
        full_path = self._get_full_path(file_path)
        return full_path.exists()

    def get_url(self, file_path: str) -> str:
        """Get file path for local storage"""
        return str(self._get_full_path(file_path))