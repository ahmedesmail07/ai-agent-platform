"""
Custom exceptions for the AI Agent Platform

This module contains domain-specific exceptions and error handling utilities.
"""

from .base import BaseDomainException
from .agent import (
    AgentNotFoundError,
    AgentValidationError,
    AgentCreationError,
    AgentUpdateError,
    AgentDeletionError,
    AgentConfigurationError,
)
from .session import (
    SessionNotFoundError,
    SessionValidationError,
    SessionCreationError,
    MessageNotFoundError,
    MessageValidationError,
    MessageCreationError,
    InvalidSenderError,
)
from .voice import (
    AudioProcessingError,
    SpeechToTextError,
    TextToSpeechError,
    UnsupportedAudioFormatError,
    AudioMetadataError,
    VoiceServiceError,
)
from .database import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseTransactionError,
    DatabaseMigrationError,
    DatabaseConstraintError,
    DatabaseTimeoutError,
)
from .openai import (
    OpenAIError,
    OpenAIAPIError,
    OpenAIKeyError,
    OpenAIQuotaExceededError,
    OpenAIRequestTimeoutError,
    OpenAIModelError,
    OpenAIChatCompletionError,
    OpenAIAudioError,
)
from .validation import (
    ValidationError,
)
from .handler import setup_exception_handlers

__all__ = [
    # Base exception
    "BaseDomainException",
    # Agent exceptions
    "AgentNotFoundError",
    "AgentValidationError",
    "AgentCreationError",
    "AgentUpdateError",
    "AgentDeletionError",
    "AgentConfigurationError",
    # Session exceptions
    "SessionNotFoundError",
    "SessionValidationError",
    "SessionCreationError",
    "MessageNotFoundError",
    "MessageValidationError",
    "MessageCreationError",
    "InvalidSenderError",
    # Voice exceptions
    "AudioProcessingError",
    "SpeechToTextError",
    "TextToSpeechError",
    "UnsupportedAudioFormatError",
    "AudioMetadataError",
    "VoiceServiceError",
    # Database exceptions
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    "DatabaseTransactionError",
    "DatabaseMigrationError",
    "DatabaseConstraintError",
    "DatabaseTimeoutError",
    # OpenAI exceptions
    "OpenAIError",
    "OpenAIAPIError",
    "OpenAIKeyError",
    "OpenAIQuotaExceededError",
    "OpenAIRequestTimeoutError",
    "OpenAIModelError",
    "OpenAIChatCompletionError",
    "OpenAIAudioError",
    # Validation exceptions
    "ValidationError",
    # Error handler setup
    "setup_exception_handlers",
]
