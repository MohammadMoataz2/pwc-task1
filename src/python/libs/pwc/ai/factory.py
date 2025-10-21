from typing import Dict, Type
from .base import AIInterface
from .openai_client import OpenAIClient


class AIFactory:
    """Factory class for creating AI client instances"""

    _ai_classes: Dict[str, Type[AIInterface]] = {
        "openai": OpenAIClient,
        # "huggingface": HuggingFaceClient,  # Future implementation
    }

    @classmethod
    def create_client(cls, ai_provider: str, **kwargs) -> AIInterface:
        """Create AI client instance based on provider type"""
        if ai_provider not in cls._ai_classes:
            raise ValueError(
                f"Unknown AI provider: {ai_provider}. "
                f"Available providers: {list(cls._ai_classes.keys())}"
            )

        ai_class = cls._ai_classes[ai_provider]
        return ai_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, ai_class: Type[AIInterface]):
        """Register a new AI provider implementation"""
        cls._ai_classes[name] = ai_class