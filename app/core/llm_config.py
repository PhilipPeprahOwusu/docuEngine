"""LLM Configuration and Initialization"""
from app.core.config import settings
from app.llm import LLMProviderFactory, BaseLLMProvider
from typing import Optional


def get_llm_provider(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> BaseLLMProvider:
    """
    Get configured LLM provider instance.

    Args:
        provider: Override provider from settings (openai, gemini, anthropic)
        api_key: Override API key from settings
        model: Override model from settings
        temperature: Override temperature from settings
        max_tokens: Override max_tokens from settings

    Returns:
        Configured LLM provider instance

    Raises:
        ValueError: If provider not configured or API key missing
    """
    # Use provided values or fall back to settings
    provider_name = provider or settings.LLM_PROVIDER

    # Get API key for selected provider
    if api_key:
        selected_api_key = api_key
    else:
        api_keys = {
            "openai": settings.OPENAI_API_KEY,
            "gemini": settings.GEMINI_API_KEY,
            "anthropic": settings.ANTHROPIC_API_KEY
        }
        selected_api_key = api_keys.get(provider_name.lower())

        if not selected_api_key:
            raise ValueError(
                f"API key not configured for provider '{provider_name}'. "
                f"Please set {provider_name.upper()}_API_KEY in your .env file."
            )

    # Use provided values or defaults
    model_name = model or settings.DEFAULT_MODEL or None
    temp = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
    tokens = max_tokens if max_tokens is not None else settings.DEFAULT_MAX_TOKENS

    return LLMProviderFactory.create_provider(
        provider_name=provider_name,
        api_key=selected_api_key,
        model=model_name,
        temperature=temp,
        max_tokens=tokens
    )


def get_available_providers() -> dict:
    """
    Get information about all available LLM providers.

    Returns:
        Dict with provider info including available models
    """
    return LLMProviderFactory.get_provider_info()
