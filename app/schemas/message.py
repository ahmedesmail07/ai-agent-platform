from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AudioMetadataResponse(BaseModel):
    """Schema for audio metadata response"""

    id: int
    message_id: int
    input_audio_path: Optional[str] = None
    output_audio_path: Optional[str] = None
    input_audio_format: Optional[str] = None
    output_audio_format: Optional[str] = None
    input_audio_duration: Optional[int] = None
    output_audio_duration: Optional[int] = None
    transcription_text: Optional[str] = None
    tts_voice: Optional[str] = None
    additional_metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base Message schema"""

    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Schema for creating a message"""

    pass


class MessageResponse(MessageBase):
    """Schema for message response"""

    id: int
    session_id: int
    sender: Literal["user", "agent"]
    created_at: datetime
    audio_metadata: Optional[AudioMetadataResponse] = None

    class Config:
        from_attributes = True


class UserMessageCreate(MessageBase):
    """Schema for user message creation"""

    pass


class AgentResponse(BaseModel):
    """Schema for agent response"""

    message: str
    session_id: int


class UserMessageWithKnowledgeBase(UserMessageCreate):
    knowledge_base: Optional[str] = None  # New optional field
