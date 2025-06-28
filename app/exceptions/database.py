"""
Database-related exceptions for the AI Agent Platform

This module contains exceptions specific to database operations.
"""

from .base import BaseDomainException


class DatabaseError(BaseDomainException):
    """Base exception for database errors."""

    def __init__(self, message: str, operation: str = None):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, message: str = None, database_url: str = None):
        details = {"database_url": database_url} if database_url else {}
        super().__init__(
            message=message or "Failed to connect to database",
            error_code="DATABASE_CONNECTION_ERROR",
            status_code=500,
            details=details,
        )


class DatabaseQueryError(DatabaseError):
    """Raised when a database query fails."""

    def __init__(self, message: str, query: str = None, params: dict = None):
        details = {}
        if query:
            details["query"] = query
        if params:
            details["params"] = params

        super().__init__(
            message=message,
            error_code="DATABASE_QUERY_ERROR",
            status_code=500,
            details=details,
        )


class DatabaseTransactionError(DatabaseError):
    """Raised when a database transaction fails."""

    def __init__(self, message: str, transaction_id: str = None):
        details = {"transaction_id": transaction_id} if transaction_id else {}
        super().__init__(
            message=message,
            error_code="DATABASE_TRANSACTION_ERROR",
            status_code=500,
            details=details,
        )


class DatabaseMigrationError(DatabaseError):
    """Raised when database migration fails."""

    def __init__(self, message: str, migration_version: str = None):
        details = {"migration_version": migration_version} if migration_version else {}
        super().__init__(
            message=message,
            error_code="DATABASE_MIGRATION_ERROR",
            status_code=500,
            details=details,
        )


class DatabaseConstraintError(DatabaseError):
    """Raised when a database constraint is violated."""

    def __init__(self, message: str, constraint: str = None, table: str = None):
        details = {}
        if constraint:
            details["constraint"] = constraint
        if table:
            details["table"] = table

        super().__init__(
            message=message,
            error_code="DATABASE_CONSTRAINT_ERROR",
            status_code=400,
            details=details,
        )


class DatabaseTimeoutError(DatabaseError):
    """Raised when a database operation times out."""

    def __init__(self, message: str, timeout_seconds: int = None):
        details = {"timeout_seconds": timeout_seconds} if timeout_seconds else {}
        super().__init__(
            message=message,
            error_code="DATABASE_TIMEOUT_ERROR",
            status_code=500,
            details=details,
        )
