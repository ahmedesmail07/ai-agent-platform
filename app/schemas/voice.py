from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class VoiceResponse(BaseModel):
    """Schema for voice response"""

    message: str
    session_id: int
    audio_url: str
    transcription: str


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
    additional_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
