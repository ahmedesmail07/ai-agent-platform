"""
Session-related exceptions for the AI Agent Platform

This module contains exceptions specific to chat sessions and messages.
"""

from .base import BaseDomainException


class SessionNotFoundError(BaseDomainException):
    """Raised when a chat session is not found in the database."""

    def __init__(self, session_id: int, message: str = None):
        super().__init__(
            message=message or f"Session with ID {session_id} not found",
            error_code="SESSION_NOT_FOUND",
            status_code=404,
            details={"session_id": session_id},
        )


class SessionValidationError(BaseDomainException):
    """Raised when session data validation fails."""

    def __init__(self, message: str, field: str = None, value: str = None):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value

        super().__init__(
            message=message,
            error_code="SESSION_VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class SessionCreationError(BaseDomainException):
    """Raised when session creation fails."""

    def __init__(self, agent_id: int, message: str = None):
        super().__init__(
            message=message or f"Failed to create session for agent {agent_id}",
            error_code="SESSION_CREATION_ERROR",
            status_code=500,
            details={"agent_id": agent_id},
        )


class MessageNotFoundError(BaseDomainException):
    """Raised when a message is not found in the database."""

    def __init__(self, message_id: int, message: str = None):
        super().__init__(
            message=message or f"Message with ID {message_id} not found",
            error_code="MESSAGE_NOT_FOUND",
            status_code=404,
            details={"message_id": message_id},
        )


class MessageValidationError(BaseDomainException):
    """Raised when message data validation fails."""

    def __init__(self, message: str, field: str = None, value: str = None):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value

        super().__init__(
            message=message,
            error_code="MESSAGE_VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class MessageCreationError(BaseDomainException):
    """Raised when message creation fails."""

    def __init__(self, session_id: int, message: str = None):
        super().__init__(
            message=message or f"Failed to create message for session {session_id}",
            error_code="MESSAGE_CREATION_ERROR",
            status_code=500,
            details={"session_id": session_id},
        )


class InvalidSenderError(BaseDomainException):
    """Raised when an invalid sender is specified for a message."""

    def __init__(self, sender: str, message: str = None):
        super().__init__(
            message=message or f"Invalid sender '{sender}'. Must be 'user' or 'agent'",
            error_code="INVALID_SENDER",
            status_code=400,
            details={"sender": sender, "valid_senders": ["user", "agent"]},
        )
