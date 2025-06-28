from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AudioMetadata(BaseModel):
    """Audio metadata model for voice interactions"""

    __tablename__ = "audio_metadata"

    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    input_audio_path = Column(String(500), nullable=True)
    output_audio_path = Column(String(500), nullable=True)
    input_audio_format = Column(String(10), nullable=True)  # wav, mp3, etc.
    output_audio_format = Column(String(10), nullable=True)
    input_audio_duration = Column(Integer, nullable=True)  # in seconds
    output_audio_duration = Column(Integer, nullable=True)  # in seconds
    transcription_text = Column(Text, nullable=True)
    tts_voice = Column(String(50), nullable=True)  # alloy, echo, fable, etc.
    additional_metadata = Column(JSON, nullable=True)  # Additional metadata

    # Relationships
    message = relationship("Message", back_populates="audio_metadata")
