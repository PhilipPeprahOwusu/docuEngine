"""Company Policy Database Model"""
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class CompanyPolicy(Base):
    """Company Policy model for policy-based evaluation"""
    __tablename__ = "company_policies"

    policy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False, index=True)
    policy_name = Column(String(255), nullable=False)
    policy_description = Column(Text)
    policy_document = Column(Text)  # Full policy text
    policy_rules = Column(JSONB)  # Extracted rules in structured format
    version = Column(String(50))
    effective_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    status = Column(String(50), default="active")  # active, archived

    # Relationships
    organization = relationship("Organization", back_populates="company_policies")
    violations = relationship("PolicyViolation", back_populates="policy")
    policy_exceptions = relationship("PolicyException", back_populates="policy")
