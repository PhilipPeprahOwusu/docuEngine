"""Custom Agent Database Model"""
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class CustomAgent(Base):
    """Custom Agent model for user-created agents"""
    __tablename__ = "custom_agents"

    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    agent_description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    available_tools = Column(ARRAY(Text))  # List of tool names
    model = Column(String(100), default="claude-3-5-sonnet-20241022")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    status = Column(String(50), default="active")  # active, archived

    # Relationships
    organization = relationship("Organization", back_populates="custom_agents")
