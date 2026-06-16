"""Policy Exception Database Model"""
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class PolicyException(Base):
    """Policy Exception model for approved violations"""
    __tablename__ = "policy_exceptions"

    exception_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False, index=True)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("company_policies.policy_id"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("policy_violations_with_citations.violation_id"))

    exception_reason = Column(Text)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    approval_timestamp = Column(DateTime(timezone=True))
    rejection_reason = Column(Text, nullable=True)
    valid_until = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="policy_exceptions")
    policy = relationship("CompanyPolicy", back_populates="policy_exceptions")
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", back_populates="approved_exceptions", foreign_keys=[approved_by])
