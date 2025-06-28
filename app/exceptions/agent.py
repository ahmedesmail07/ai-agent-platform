"""
Agent-related exceptions for the AI Agent Platform

This module contains exceptions specific to agent operations.
"""

from .base import BaseDomainException


class AgentNotFoundError(BaseDomainException):
    """Raised when an agent is not found in the database."""

    def __init__(self, agent_id: int, message: str = None):
        super().__init__(
            message=message or f"Agent with ID {agent_id} not found",
            error_code="AGENT_NOT_FOUND",
            status_code=404,
            details={"agent_id": agent_id},
        )


class AgentValidationError(BaseDomainException):
    """Raised when agent validation fails."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            error_code="AGENT_VALIDATION_ERROR",
            status_code=400,
            details=details or {},
        )


class AgentCreationError(BaseDomainException):
    """Raised when agent creation fails."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            error_code="AGENT_CREATION_ERROR",
            status_code=500,
            details=details or {},
        )


class AgentUpdateError(BaseDomainException):
    """Raised when agent update fails."""

    def __init__(self, agent_id: int, message: str = None):
        super().__init__(
            message=message or f"Failed to update agent with ID {agent_id}",
            error_code="AGENT_UPDATE_ERROR",
            status_code=500,
            details={"agent_id": agent_id},
        )


class AgentDeletionError(BaseDomainException):
    """Raised when agent deletion fails."""

    def __init__(self, agent_id: int, message: str = None):
        super().__init__(
            message=message or f"Failed to delete agent with ID {agent_id}",
            error_code="AGENT_DELETION_ERROR",
            status_code=500,
            details={"agent_id": agent_id},
        )


class AgentConfigurationError(BaseDomainException):
    """Raised when agent configuration is invalid."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            error_code="AGENT_CONFIGURATION_ERROR",
            status_code=400,
            details=details or {},
        )
