"""
Voice-related exceptions for the AI Agent Platform

This module contains exceptions specific to voice processing, speech-to-text,
and text-to-speech operations.
"""

from .base import BaseDomainException


class AudioProcessingError(BaseDomainException):
    """Base exception for audio processing errors."""

    def __init__(self, message: str, audio_file: str = None):
        details = {"audio_file": audio_file} if audio_file else {}
        super().__init__(
            message=message,
            error_code="AUDIO_PROCESSING_ERROR",
            status_code=500,
            details=details,
        )


class SpeechToTextError(AudioProcessingError):
    """Raised when speech-to-text conversion fails."""

    def __init__(self, message: str, audio_file: str = None, original_error: str = None):
        details = {}
        if audio_file:
            details["audio_file"] = audio_file
        if original_error:
            details["original_error"] = original_error

        super().__init__(
            message=message,
            audio_file=audio_file,
        )
        self.error_code = "SPEECH_TO_TEXT_ERROR"
        self.details.update(details)


class TextToSpeechError(AudioProcessingError):
    """Raised when text-to-speech conversion fails."""

    def __init__(self, message: str, text: str = None, original_error: str = None):
        details = {}
        if text:
            details["text"] = text
        if original_error:
            details["original_error"] = original_error

        super().__init__(
            message=message,
            audio_file=None,
        )
        self.error_code = "TEXT_TO_SPEECH_ERROR"
        self.details.update(details)


class UnsupportedAudioFormatError(BaseDomainException):
    """Raised when an unsupported audio format is provided."""

    def __init__(self, file_extension: str, supported_formats: list = None, message: str = None):
        supported = supported_formats or [".wav", ".mp3", ".m4a", ".webm"]
        supported_str = ", ".join(supported)
        super().__init__(
            message=message
            or f"Unsupported audio format '{file_extension}'. "
            f"Supported formats: {supported_str}",
            error_code="UNSUPPORTED_AUDIO_FORMAT",
            status_code=400,
            details={
                "file_extension": file_extension,
                "supported_formats": supported,
            },
        )


class AudioMetadataError(BaseDomainException):
    """Raised when audio metadata operations fail."""

    def __init__(self, message: str, message_id: int = None):
        details = {"message_id": message_id} if message_id else {}
        super().__init__(
            message=message,
            error_code="AUDIO_METADATA_ERROR",
            status_code=500,
            details=details,
        )


class VoiceServiceError(BaseDomainException):
    """Raised when voice service operations fail."""

    def __init__(self, message: str, session_id: int = None):
        details = {"session_id": session_id} if session_id else {}
        super().__init__(
            message=message,
            error_code="VOICE_SERVICE_ERROR",
            status_code=500,
            details=details,
        )
