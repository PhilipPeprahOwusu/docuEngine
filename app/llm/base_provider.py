"""Base LLM Provider Interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""

    def __init__(self, api_key: str, model: str = None, temperature: float = 0.7, max_tokens: int = 2000):
        self.api_key = api_key
        self.model = model or self.get_default_model()
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def get_default_model(self) -> str:
        """Return the default model for this provider"""
        pass

    @abstractmethod
    def invoke(self, prompt: str, **kwargs) -> Any:
        """
        Send a prompt to the LLM and get a response.

        Args:
            prompt: The prompt to send
            **kwargs: Additional provider-specific parameters

        Returns:
            Response object with .content attribute
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list:
        """Return list of available models for this provider"""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(model={self.model})"
