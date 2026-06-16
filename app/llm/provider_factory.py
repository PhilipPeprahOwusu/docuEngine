"""LLM Provider Factory"""
from app.llm.base_provider import BaseLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.anthropic_provider import AnthropicProvider
from typing import Optional


class LLMProviderFactory:
    """Factory to create LLM providers based on user selection"""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "anthropic": AnthropicProvider
    }

    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        api_key: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_name: One of 'openai', 'gemini', 'anthropic'
            api_key: API key for the selected provider
            model: Optional specific model (uses default if not provided)
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Instance of the selected provider

        Raises:
            ValueError: If provider_name is not supported
        """
        provider_name = provider_name.lower()

        if provider_name not in cls.PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider_name}. "
                f"Supported providers: {', '.join(cls.PROVIDERS.keys())}"
            )

        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of all available provider names"""
        return list(cls.PROVIDERS.keys())

    @classmethod
    def get_provider_info(cls) -> dict:
        """Get information about all providers"""
        info = {}
        for name, provider_class in cls.PROVIDERS.items():
            # Create temporary instance to get model info
            temp_instance = provider_class(api_key="temp")
            info[name] = {
                "default_model": temp_instance.get_default_model(),
                "available_models": temp_instance.get_available_models()
            }
        return info
