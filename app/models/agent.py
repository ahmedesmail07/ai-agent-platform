from sqlalchemy import JSON, Boolean, Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Agent(BaseModel):
    """AI Agent model"""

    __tablename__ = "agents"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    agent_type = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    # configuration is a JSON object that contains the configuration of the agent
    # example: {"model": "gpt-4o", "max_tokens": 1000, "temperature": 0.7}
    configuration = Column(JSON, nullable=True)
    # capabilities is a JSON object that contains the capabilities of the agent
    # example: {"text_generation": true, "conversation": true}
    capabilities = Column(JSON, nullable=True, default=dict)

    # Relationships
    sessions = relationship("ChatSession", back_populates="agent")
