"""Document Database Model"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class Document(Base):
    """Document model for storing uploaded documents (contracts, policies, reports, etc.)"""
    __tablename__ = "documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    content = Column(Text, nullable=False)
    s3_key = Column(String(500))
    parties = Column(ARRAY(Text))
    document_type = Column(String(100))  # contract, policy, report, agreement, etc.
    status = Column(String(50), default="pending")  # pending, approved, active, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Finalization fields
    finalized_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    signature_data = Column(JSON, nullable=True)  # Stores digital signature info
    final_pdf_url = Column(String(500), nullable=True)  # S3 or local path to locked PDF

    # Relationships
    organization = relationship("Organization", back_populates="documents")
    creator = relationship("User", back_populates="documents_created", foreign_keys=[created_by])
    finalizer = relationship("User", foreign_keys=[finalized_by])
    violations = relationship("PolicyViolation", back_populates="document")
    custom_contexts = relationship("CustomContext", back_populates="document")
    policy_exceptions = relationship("PolicyException", back_populates="document")
    audit_logs = relationship("AuditLog", back_populates="document")
