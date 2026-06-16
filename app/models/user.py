"""User Database Model"""
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class User(Base):
    """User model with RBAC"""
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # admin, reviewer, viewer, approver
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="users")
    documents_created = relationship("Document", back_populates="creator", foreign_keys="Document.created_by")
    audit_logs = relationship("AuditLog", back_populates="user")
    notification_preferences = relationship("NotificationPreference", back_populates="user", uselist=False)
    custom_contexts = relationship("CustomContext", back_populates="user", foreign_keys="CustomContext.user_id")
    approved_exceptions = relationship("PolicyException", back_populates="approver", foreign_keys="PolicyException.approved_by")
