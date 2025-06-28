"""
Exception handler for the AI Agent Platform

This module contains the main exception handler that catches and handles
all custom exceptions in FastAPI.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from .base import BaseDomainException
from .database import DatabaseError, DatabaseConnectionError
from .openai import OpenAIError, OpenAIKeyError

logger = logging.getLogger(__name__)


async def domain_exception_handler(request: Request, exc: BaseDomainException) -> JSONResponse:
    """
    Handle domain-specific exceptions.

    Args:
        request: FastAPI request object
        exc: The domain exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"Domain exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


async def pydantic_validation_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: The Pydantic validation error

    Returns:
        JSONResponse with validation error details
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        f"Validation error: {len(errors)} field(s) failed validation",
        extra={
            "validation_errors": errors,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "details": {
                "validation_errors": errors,
            },
        },
    )


async def database_exception_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """
    Handle database-related exceptions.

    Args:
        request: FastAPI request object
        exc: The database exception

    Returns:
        JSONResponse with database error details
    """
    logger.error(
        f"Database error: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )

    if isinstance(exc, DatabaseConnectionError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "SERVICE_UNAVAILABLE",
                "message": "Database service is temporarily unavailable",
                "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
                "details": {},
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


async def openai_exception_handler(request: Request, exc: OpenAIError) -> JSONResponse:
    """
    Handle OpenAI-related exceptions.

    Args:
        request: FastAPI request object
        exc: The OpenAI exception

    Returns:
        JSONResponse with OpenAI error details
    """
    logger.error(
        f"OpenAI error: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )

    if isinstance(exc, OpenAIKeyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "AI_SERVICE_ERROR",
                "message": "AI service configuration error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "details": {},
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle generic exceptions that weren't caught by specific handlers.

    Args:
        request: FastAPI request object
        exc: The generic exception

    Returns:
        JSONResponse with generic error details
    """
    logger.error(
        f"Unexpected error: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "details": {},
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Set up all exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(BaseDomainException, domain_exception_handler)

    app.add_exception_handler(PydanticValidationError, pydantic_validation_handler)

    app.add_exception_handler(DatabaseError, database_exception_handler)

    app.add_exception_handler(OpenAIError, openai_exception_handler)

    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers have been set up successfully")
