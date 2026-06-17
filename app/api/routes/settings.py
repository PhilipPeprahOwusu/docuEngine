"""Settings API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List
from app.db.session import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.core.security import oauth2_scheme, decode_access_token
from app.core.encryption import encrypt_api_key, decrypt_api_key, get_key_preview

router = APIRouter()

# Valid model names for each provider
# Updated based on latest API documentation
VALID_MODELS: Dict[str, List[str]] = {
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4",
        "gpt-3.5-turbo"
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022",  # Latest Claude 3.5 Sonnet (Oct 2024)
        "claude-3-5-sonnet-20240620",  # Claude 3.5 Sonnet (June 2024)
        "claude-3-5-haiku-20241022",   # Claude 3.5 Haiku (Oct 2024)
        "claude-3-opus-20240229",      # Claude 3 Opus (Feb 2024) - May require higher tier
        "claude-3-sonnet-20240229",    # Claude 3 Sonnet (Feb 2024)
        "claude-3-haiku-20240307"      # Claude 3 Haiku (March 2024)
    ],
    "gemini": [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-pro"
    ]
}


class SaveAPIKeyRequest(BaseModel):
    provider: str  # openai, anthropic, gemini
    api_key: str
    model_name: str


class APIKeyResponse(BaseModel):
    provider: str
    key_preview: str
    model_name: str
    created_at: str


class NewAPIKeyResponse(BaseModel):
    provider: str
    api_key: str  # Full key shown ONCE
    key_preview: str
    model_name: str
    message: str


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    token_data = decode_access_token(token)
    if not token_data or not token_data.sub:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = db.query(User).filter(User.user_id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.get("/models")
async def get_available_models():
    """Get list of available models for each provider"""
    return {"models": VALID_MODELS}


@router.post("/api-keys", response_model=NewAPIKeyResponse)
async def save_api_key(
    request: SaveAPIKeyRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Save or update an encrypted API key (shows full key ONCE)"""

    # Validate provider
    valid_providers = ["openai", "anthropic", "gemini"]
    if request.provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {valid_providers}")

    # Validate model name
    if request.model_name not in VALID_MODELS.get(request.provider, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model '{request.model_name}' for provider '{request.provider}'. Valid models: {VALID_MODELS[request.provider]}"
        )

    # Encrypt the API key
    encrypted_key = encrypt_api_key(request.api_key)
    key_preview = get_key_preview(request.api_key)

    # Check if API key already exists for this provider
    existing_key = db.query(APIKey).filter(
        APIKey.org_id == current_user.org_id,
        APIKey.provider == request.provider
    ).first()

    if existing_key:
        # Update existing key
        existing_key.encrypted_key = encrypted_key
        existing_key.key_preview = key_preview
        existing_key.model_name = request.model_name
        message = f"{request.provider.capitalize()} API key updated successfully"
    else:
        # Create new key
        new_key = APIKey(
            org_id=current_user.org_id,
            provider=request.provider,
            encrypted_key=encrypted_key,
            key_preview=key_preview,
            model_name=request.model_name
        )
        db.add(new_key)
        message = f"{request.provider.capitalize()} API key saved successfully"

    db.commit()

    # Return the full API key ONCE
    return NewAPIKeyResponse(
        provider=request.provider,
        api_key=request.api_key,  # Full key shown only this once
        key_preview=key_preview,
        model_name=request.model_name,
        message=message
    )


@router.get("/api-keys")
async def get_api_keys(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get all API keys for the organization (returns masked previews only)"""

    api_keys = db.query(APIKey).filter(
        APIKey.org_id == current_user.org_id
    ).all()

    return {
        "api_keys": [
            {
                "provider": key.provider,
                "key_preview": key.key_preview,
                "model_name": key.model_name,
                "created_at": key.created_at.isoformat() if key.created_at else None,
                "updated_at": key.updated_at.isoformat() if key.updated_at else None
            }
            for key in api_keys
        ]
    }


@router.delete("/api-keys/{provider}")
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Delete an API key"""

    api_key = db.query(APIKey).filter(
        APIKey.org_id == current_user.org_id,
        APIKey.provider == provider
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()

    return {"message": f"{provider.capitalize()} API key deleted successfully"}


class TestAPIKeyRequest(BaseModel):
    provider: str
    api_key: str
    model_name: str


@router.post("/api-keys/list-models")
async def list_available_models(
    request: TestAPIKeyRequest,
    current_user: User = Depends(get_current_user_from_token)
):
    """Fetch available models from the provider API dynamically"""

    try:
        if request.provider == "openai":
            # OpenAI has a models API
            import openai
            client = openai.OpenAI(api_key=request.api_key)
            models_response = client.models.list()

            # Filter to only GPT models
            available_models = [
                model.id for model in models_response.data
                if model.id.startswith(('gpt-4', 'gpt-3.5'))
            ]

            return {
                "success": True,
                "provider": request.provider,
                "models": sorted(available_models, reverse=True)  # Latest first
            }

        elif request.provider == "anthropic":
            # Anthropic doesn't have a models list API, so we test common models
            from langchain_anthropic import ChatAnthropic

            # Models to test (ordered by release date, newest first)
            models_to_test = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-5-sonnet-20240620",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]

            available_models = []
            errors = []

            for model in models_to_test:
                try:
                    # Quick test with minimal tokens
                    llm = ChatAnthropic(
                        model=model,
                        api_key=request.api_key,
                        temperature=0,
                        max_tokens=10
                    )
                    llm.invoke("test")
                    available_models.append(model)
                    print(f"✅ Model {model} is accessible")
                except Exception as e:
                    # Model not available, log the error
                    error_msg = str(e)
                    print(f"❌ Model {model} failed: {error_msg[:200]}")
                    errors.append({"model": model, "error": error_msg[:200]})
                    continue

            if not available_models:
                # Include first error in message for debugging
                error_detail = ""
                if errors:
                    first_error = errors[0]["error"]
                    if "authentication" in first_error.lower() or "401" in first_error:
                        error_detail = " (Invalid API key or authentication failed)"
                    elif "not_found" in first_error.lower() or "404" in first_error:
                        error_detail = f" (Model access restricted - check your API tier)"
                    elif "403" in first_error or "forbidden" in first_error.lower():
                        error_detail = " (Access forbidden - insufficient permissions)"
                    else:
                        error_detail = f" ({first_error[:100]})"

                return {
                    "success": False,
                    "message": f"No Claude models are accessible with this API key{error_detail}",
                    "models": [],
                    "errors": errors[:3]  # Return first 3 errors for debugging
                }

            return {
                "success": True,
                "provider": request.provider,
                "models": available_models
            }

        elif request.provider == "gemini":
            # Gemini models list
            # Google doesn't have a simple list endpoint, so we provide known models
            available_models = [
                "gemini-1.5-pro-latest",
                "gemini-1.5-flash-latest",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro"
            ]

            return {
                "success": True,
                "provider": request.provider,
                "models": available_models
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to fetch models: {str(e)}",
            "models": []
        }


@router.post("/api-keys/test")
async def test_api_key(
    request: TestAPIKeyRequest,
    current_user: User = Depends(get_current_user_from_token)
):
    """Test if an API key works before saving it"""

    # Validate provider
    if request.provider not in VALID_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {request.provider}")

    try:
        # Try to initialize the LLM with the provided credentials
        from langchain_anthropic import ChatAnthropic
        from langchain_openai import ChatOpenAI
        from langchain_google_genai import ChatGoogleGenerativeAI

        if request.provider == "anthropic":
            llm = ChatAnthropic(
                model=request.model_name,
                api_key=request.api_key,
                temperature=0,
                max_tokens=100
            )
        elif request.provider == "openai":
            llm = ChatOpenAI(
                model=request.model_name,
                api_key=request.api_key,
                temperature=0,
                max_tokens=100
            )
        elif request.provider == "gemini":
            llm = ChatGoogleGenerativeAI(
                model=request.model_name,
                google_api_key=request.api_key,
                temperature=0,
                max_output_tokens=100
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        # Test with a simple prompt
        response = llm.invoke("Say 'API key is valid' if you can read this.")

        return {
            "success": True,
            "message": f"{request.provider.capitalize()} API key is valid and working with model {request.model_name}",
            "test_response": response.content[:100]  # Show first 100 chars of response
        }

    except Exception as e:
        error_message = str(e)

        # Parse common error messages
        if "404" in error_message or "not_found_error" in error_message.lower():
            return {
                "success": False,
                "message": f"Model '{request.model_name}' not found or not accessible with your API key.",
                "error": error_message
            }
        elif "401" in error_message or "authentication" in error_message.lower():
            return {
                "success": False,
                "message": "Invalid API key. Please check your credentials.",
                "error": error_message
            }
        elif "403" in error_message or "forbidden" in error_message.lower():
            return {
                "success": False,
                "message": "Access denied. Your API key may not have permission to use this model.",
                "error": error_message
            }
        else:
            return {
                "success": False,
                "message": "API key test failed",
                "error": error_message
            }
