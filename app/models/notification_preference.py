"""Notification Preference Database Model"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class NotificationPreference(Base):
    """User Notification Preferences model"""
    __tablename__ = "user_notification_preferences"

    preference_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, unique=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False)

    # Channel configurations
    slack_enabled = Column(Boolean, default=True)
    slack_workspace_token = Column(String)  # Encrypted
    slack_channel_id = Column(String)
    slack_user_id = Column(String)

    email_enabled = Column(Boolean, default=True)
    email_address = Column(String(255))

    discord_enabled = Column(Boolean, default=False)
    discord_server_id = Column(String)  # Encrypted
    discord_channel_id = Column(String)
    discord_user_id = Column(String)

    # Notification types
    notify_on_violations = Column(Boolean, default=True)
    notify_on_contradictions = Column(Boolean, default=True)
    notify_on_approvals = Column(Boolean, default=True)
    notify_on_policy_changes = Column(Boolean, default=False)

    # Frequency
    batching_enabled = Column(Boolean, default=False)
    batch_interval = Column(String(50), default="immediate")  # immediate, hourly, daily

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notification_preferences")
