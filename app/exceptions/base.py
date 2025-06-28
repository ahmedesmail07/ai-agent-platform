"""
Base domain exception for the AI Agent Platform

This module contains the base exception class that all domain-specific exceptions inherit from.
"""

from typing import Any, Dict, Optional


class BaseDomainException(Exception):
    """
    Base exception class for all domain-specific exceptions.

    This class provides a consistent structure for error handling across the application.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the base domain exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for programmatic handling
            status_code: HTTP status code for API responses
            details: Additional error details for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the exception
        """
        return {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }

    def __str__(self) -> str:
        """String representation of the exception."""
        return f"{self.error_code}: {self.message}"

    def __repr__(self) -> str:
        """Detailed string representation of the exception."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"status_code={self.status_code}, "
            f"details={self.details})"
        )
