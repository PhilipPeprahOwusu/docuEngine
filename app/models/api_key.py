"""API Key Model for secure credential storage"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class APIKey(Base):
    """Encrypted API key storage for LLM providers"""
    __tablename__ = "api_keys"

    key_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # openai, anthropic, gemini
    encrypted_key = Column(Text, nullable=False)  # AES encrypted API key
    key_preview = Column(String(20), nullable=False)  # Last 4 chars for display (e.g., "...abc123")
    model_name = Column(String(100))  # Selected model
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="api_keys")
