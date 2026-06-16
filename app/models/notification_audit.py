"""Notification Audit Database Model"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class NotificationAudit(Base):
    """Notification Audit model for tracking all notifications"""
    __tablename__ = "notification_audit"

    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    event_type = Column(String(100))
    channel = Column(String(50))  # slack, email, discord
    status = Column(String(50), index=True)  # sent, delivered, clicked, approved, rejected
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"))
    exception_id = Column(UUID(as_uuid=True), ForeignKey("policy_exceptions.exception_id"))
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True))
    interacted_at = Column(DateTime(timezone=True))
    interaction_action = Column(String(100))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
