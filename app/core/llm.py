"""LLM Configuration and Initialization"""
from app.core.config import settings
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm():
    """Get configured LLM based on settings"""
    provider = settings.LLM_PROVIDER.lower()

    if provider == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        model = settings.DEFAULT_MODEL or "claude-3-5-sonnet-20241022"
        return ChatAnthropic(
            model=model,
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            api_key=settings.ANTHROPIC_API_KEY
        )

    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")

        model = settings.DEFAULT_MODEL or "gpt-4-turbo-preview"
        return ChatOpenAI(
            model=model,
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY
        )

    elif provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        model = settings.DEFAULT_MODEL or "gemini-1.5-pro"
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=settings.DEFAULT_TEMPERATURE,
            max_output_tokens=settings.DEFAULT_MAX_TOKENS,
            google_api_key=settings.GEMINI_API_KEY
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
