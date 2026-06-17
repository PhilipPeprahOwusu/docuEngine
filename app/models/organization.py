"""Organization Database Model"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class Organization(Base):
    """Organization model for multi-tenancy"""
    __tablename__ = "organizations"

    org_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    plan = Column(String(50))  # free, professional, enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")
    documents = relationship("Document", back_populates="organization")
    company_policies = relationship("CompanyPolicy", back_populates="organization")
    custom_agents = relationship("CustomAgent", back_populates="organization")
    audit_logs = relationship("AuditLog", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
