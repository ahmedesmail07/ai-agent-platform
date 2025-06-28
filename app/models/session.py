from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

# TODO: Enum for sender
# class Sender(Enum):
#     USER = "user"
#     AGENT = "agent"
#     SYSTEM = "system"


class ChatSession(BaseModel):
    """Chat session model"""

    __tablename__ = "chat_sessions"

    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    # Relationships
    agent = relationship("Agent", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(BaseModel):
    """Message model"""

    __tablename__ = "messages"

    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'agent'
    content = Column(Text, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    audio_metadata = relationship(
        "AudioMetadata",
        back_populates="message",
        uselist=False,
        cascade="all, delete-orphan",
    )
