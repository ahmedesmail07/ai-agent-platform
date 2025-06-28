"""
OpenAI-related exceptions for the AI Agent Platform

This module contains exceptions specific to OpenAI API operations.
"""

from .base import BaseDomainException


class OpenAIError(BaseDomainException):
    """Base exception for OpenAI-related errors."""

    def __init__(self, message: str, api_endpoint: str = None):
        details = {"api_endpoint": api_endpoint} if api_endpoint else {}
        super().__init__(
            message=message,
            error_code="OPENAI_ERROR",
            status_code=500,
            details=details,
        )


class OpenAIAPIError(OpenAIError):
    """Raised when OpenAI API returns an error."""

    def __init__(self, message: str, status_code: int = None, api_response: dict = None):
        details = {}
        if status_code:
            details["openai_status_code"] = status_code
        if api_response:
            details["api_response"] = api_response

        super().__init__(
            message=message,
            api_endpoint=None,
        )
        self.error_code = "OPENAI_API_ERROR"
        if status_code:
            self.status_code = status_code
        self.details.update(details)


class OpenAIKeyError(OpenAIError):
    """Raised when OpenAI API key is invalid or missing."""

    def __init__(self, message: str = None):
        super().__init__(
            message=message or "Invalid or missing OpenAI API key",
            api_endpoint=None,
        )
        self.error_code = "OPENAI_KEY_ERROR"


class OpenAIQuotaExceededError(OpenAIError):
    """Raised when OpenAI API quota is exceeded."""

    def __init__(self, message: str = None, quota_limit: str = None):
        details = {"quota_limit": quota_limit} if quota_limit else {}
        super().__init__(
            message=message or "OpenAI API quota exceeded",
            api_endpoint=None,
        )
        self.error_code = "OPENAI_QUOTA_EXCEEDED"
        self.status_code = 429
        self.details.update(details)


class OpenAIRequestTimeoutError(OpenAIError):
    """Raised when OpenAI API request times out."""

    def __init__(self, message: str = None, timeout_seconds: int = None):
        details = {"timeout_seconds": timeout_seconds} if timeout_seconds else {}
        super().__init__(
            message=message or "OpenAI API request timed out",
            api_endpoint=None,
        )
        self.error_code = "OPENAI_TIMEOUT_ERROR"
        self.status_code = 408
        self.details.update(details)


class OpenAIModelError(OpenAIError):
    """Raised when there's an issue with the OpenAI model."""

    def __init__(self, message: str, model: str = None):
        details = {"model": model} if model else {}
        super().__init__(
            message=message,
            api_endpoint=None,
        )
        self.error_code = "OPENAI_MODEL_ERROR"
        self.status_code = 400
        self.details.update(details)


class OpenAIChatCompletionError(OpenAIError):
    """Raised when chat completion fails."""

    def __init__(self, message: str, model: str = None, messages_count: int = None):
        details = {}
        if model:
            details["model"] = model
        if messages_count:
            details["messages_count"] = messages_count

        super().__init__(
            message=message,
            api_endpoint=None,
        )
        self.error_code = "OPENAI_CHAT_COMPLETION_ERROR"
        self.details.update(details)


class OpenAIAudioError(OpenAIError):
    """Raised when OpenAI audio operations fail."""

    def __init__(self, message: str, operation: str = None):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            api_endpoint=None,
        )
        self.error_code = "OPENAI_AUDIO_ERROR"
        self.details.update(details)
