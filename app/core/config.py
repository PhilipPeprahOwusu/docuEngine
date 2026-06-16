"""Application Configuration"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for Contract Intelligence Platform"""

    # Project Information
    PROJECT_NAME: str = "Contract Intelligence Agent Platform"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "Enterprise-grade policy-governed contract management with AI agents"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3026",
        "http://localhost:8000",
        "https://frontend-eta-sepia-76.vercel.app",
        "*"  # Allow all origins (restrict in production)
    ]

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/contract_intelligence"

    # LLM Configuration - User selects provider explicitly
    LLM_PROVIDER: str = "openai"  # Options: openai, gemini, anthropic

    # API Keys - User provides key for selected provider
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # LLM Parameters
    DEFAULT_MODEL: str = ""  # Leave empty to use provider default
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2000

    # Vector Database (Qdrant)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""  # Optional

    # Cloud Storage Configuration
    STORAGE_PROVIDER: str = "gcp"  # Options: gcp, aws, local

    # AWS Configuration (if using AWS)
    AWS_REGION: str = "us-east-1"
    AWS_ACCOUNT_ID: str = ""
    S3_BUCKET: str = "contract-intelligence-docs"

    # GCP Configuration (if using GCP)
    GCP_PROJECT_ID: str = "docu-engine-499519"
    GCS_BUCKET: str = "docuengine-documents"
    GCP_CREDENTIALS_PATH: str = ""  # Path to service account JSON (optional if using workload identity)

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Notifications
    SLACK_BOT_TOKEN: str = ""
    SLACK_SIGNING_SECRET: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""

    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: str = ""

    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
