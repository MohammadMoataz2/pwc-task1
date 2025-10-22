from typing import Dict, Type
from .base import StorageInterface
from .local import LocalStorage


class StorageFactory:
    """Factory class for creating storage instances"""

    _storage_classes: Dict[str, Type[StorageInterface]] = {
        "local": LocalStorage,
        # "s3": S3Storage,  # Future implementation
    }

    @classmethod
    def create_storage(cls, storage_type: str, **kwargs) -> StorageInterface:
        """Create storage instance based on type"""
        if storage_type not in cls._storage_classes:
            raise ValueError(
                f"Unknown storage type: {storage_type}. "
                f"Available types: {list(cls._storage_classes.keys())}"
            )

        storage_class = cls._storage_classes[storage_type]
        return storage_class(**kwargs)

    @classmethod
    def register_storage(cls, name: str, storage_class: Type[StorageInterface]):
        """Register a new storage implementation"""
        cls._storage_classes[name] = storage_class