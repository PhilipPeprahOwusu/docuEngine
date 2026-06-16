"""Audit Log Database Model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class AuditLog(Base):
    """Immutable Audit Log model"""
    __tablename__ = "audit_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"))
    policy_id = Column(UUID(as_uuid=True), ForeignKey("company_policies.policy_id"))
    exception_id = Column(UUID(as_uuid=True), ForeignKey("policy_exceptions.exception_id"))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("custom_agents.agent_id"))
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    duration_ms = Column(Integer)
    result_summary = Column(String(500))
    details = Column(JSONB)

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    document = relationship("Document", back_populates="audit_logs")
