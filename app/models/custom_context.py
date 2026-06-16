"""Custom Context Database Model"""
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class CustomContext(Base):
    """Custom Context model for user-added context with validation"""
    __tablename__ = "custom_context"

    context_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    context_text = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    approval_reason = Column(Text)
    exception_valid_until = Column(Date)

    # Relationships
    document = relationship("Document", back_populates="custom_contexts")
    user = relationship("User", back_populates="custom_contexts", foreign_keys=[user_id])
