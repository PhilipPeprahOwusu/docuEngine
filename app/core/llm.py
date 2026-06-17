"""LLM Configuration and Initialization"""
from app.core.config import settings
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm import Session
from typing import Optional


def get_llm(db: Optional[Session] = None, org_id: Optional[str] = None):
    """Get configured LLM based on database settings or environment variables

    Args:
        db: Database session (optional). If provided with org_id, will check database for API keys
        org_id: Organization ID (optional). If provided with db, will fetch org-specific API keys

    Returns:
        Configured LLM instance or None if no API keys are configured
    """
    # Try to get API keys from database first (if db and org_id provided)
    api_key = None
    model_name = None
    provider = None

    if db and org_id:
        from app.models.api_key import APIKey
        from app.core.encryption import decrypt_api_key

        # Try each provider in order: OpenAI, Anthropic, Gemini
        for prov in ["openai", "anthropic", "gemini"]:
            db_key = db.query(APIKey).filter(
                APIKey.org_id == org_id,
                APIKey.provider == prov
            ).first()

            if db_key:
                try:
                    api_key = decrypt_api_key(db_key.encrypted_key)
                    model_name = db_key.model_name
                    provider = prov
                    break
                except Exception:
                    # Decryption failed, try next provider
                    continue

    # Fall back to environment variables if no database key found
    if not api_key:
        provider = settings.LLM_PROVIDER.lower()

        if provider == "anthropic":
            api_key = settings.ANTHROPIC_API_KEY
            model_name = settings.DEFAULT_MODEL or "claude-3-5-sonnet-20241022"
        elif provider == "openai":
            api_key = settings.OPENAI_API_KEY
            model_name = settings.DEFAULT_MODEL or "gpt-4-turbo-preview"
        elif provider == "gemini":
            api_key = settings.GEMINI_API_KEY
            model_name = settings.DEFAULT_MODEL or "gemini-1.5-pro"

    # Return None if no API key configured (agents will use mock data)
    if not api_key:
        return None

    # Initialize the appropriate LLM
    if provider == "anthropic":
        return ChatAnthropic(
            model=model_name or "claude-3-5-sonnet-20241022",
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            api_key=api_key
        )

    elif provider == "openai":
        return ChatOpenAI(
            model=model_name or "gpt-4-turbo-preview",
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            api_key=api_key
        )

    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=model_name or "gemini-1.5-pro",
            temperature=settings.DEFAULT_TEMPERATURE,
            max_output_tokens=settings.DEFAULT_MAX_TOKENS,
            google_api_key=api_key
        )

    else:
        return None
