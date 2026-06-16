"""Policy Violation Database Model"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class PolicyViolation(Base):
    """Policy Violation model with full citations"""
    __tablename__ = "policy_violations_with_citations"

    violation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False, index=True)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("company_policies.policy_id"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)

    # Policy Citation
    policy_name = Column(String(255))
    policy_version = Column(String(50))
    policy_section = Column(String(100))
    policy_page = Column(Integer)
    policy_quote = Column(Text)  # Exact quote from policy

    # Document Citation
    document_name = Column(String(255))
    violation_text = Column(Text)  # Exact text from document
    violation_section = Column(String(100))
    violation_page = Column(Integer)
    violation_paragraph = Column(Integer)

    # Analysis
    severity = Column(String(20), index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    violation_type = Column(String(100))
    policy_value = Column(String(255))
    actual_value = Column(String(255))
    difference = Column(String(255))
    impact_description = Column(Text)

    # Audit
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    detected_by_agent = Column(String(100))
    policy_version_at_detection = Column(String(50))
    document_version_at_detection = Column(String(50))

    # References
    policy_document_url = Column(Text)
    document_url = Column(Text)

    # Relationships
    document = relationship("Document", back_populates="violations")
    policy = relationship("CompanyPolicy", back_populates="violations")
