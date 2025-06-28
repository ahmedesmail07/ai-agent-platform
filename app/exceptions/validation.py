"""
Validation-related exceptions for the AI Agent Platform

This module contains exceptions specific to input validation.
"""

from .base import BaseDomainException


class ValidationError(BaseDomainException):
    """Base exception for validation errors."""

    def __init__(self, message: str, field: str = None, value: str = None):
        details = {}
        if field is not None:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )
