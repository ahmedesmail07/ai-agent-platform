"""
Tests for custom exceptions and error handling

This module tests the custom exception classes and their behavior.
"""

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
import pytest

from app.exceptions import (
    AgentNotFoundError,
    SessionNotFoundError,
    UnsupportedAudioFormatError,
    ValidationError,
    setup_exception_handlers,
)


class TestCustomExceptions:
    """Test custom exception classes"""

    def test_agent_not_found_error(self):
        """Test AgentNotFoundError exception"""
        error = AgentNotFoundError(123)

        assert error.message == "Agent with ID 123 not found"
        assert error.error_code == "AGENT_NOT_FOUND"
        assert error.status_code == 404
        assert error.details == {"agent_id": 123}

        # Test to_dict method
        error_dict = error.to_dict()
        assert error_dict["error"] == "AGENT_NOT_FOUND"
        assert error_dict["message"] == "Agent with ID 123 not found"
        assert error_dict["status_code"] == 404
        assert error_dict["details"] == {"agent_id": 123}

    def test_session_not_found_error(self):
        """Test SessionNotFoundError exception"""
        error = SessionNotFoundError(456)

        assert error.message == "Session with ID 456 not found"
        assert error.error_code == "SESSION_NOT_FOUND"
        assert error.status_code == 404
        assert error.details == {"session_id": 456}

    def test_unsupported_audio_format_error(self):
        """Test UnsupportedAudioFormatError exception"""
        error = UnsupportedAudioFormatError(".txt")

        assert "Unsupported audio format '.txt'" in error.message
        assert error.error_code == "UNSUPPORTED_AUDIO_FORMAT"
        assert error.status_code == 400
        assert error.details["file_extension"] == ".txt"
        assert ".wav" in error.details["supported_formats"]

    def test_validation_error(self):
        """Test ValidationError exception"""
        error = ValidationError("Invalid input", field="name", value="")

        assert error.message == "Invalid input"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.status_code == 400
        assert error.details["field"] == "name"
        assert "value" in error.details


class TestExceptionHandlers:
    """Test exception handlers in FastAPI"""

    @pytest.mark.asyncio
    async def test_domain_exception_handler(self):
        """Test that domain exceptions are handled correctly"""
        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/test-agent-not-found")
        def test_agent_not_found():
            raise AgentNotFoundError(123)

        @app.get("/test-session-not-found")
        def test_session_not_found():
            raise SessionNotFoundError(456)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test agent not found
            response = await client.get("/test-agent-not-found")
            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "AGENT_NOT_FOUND"
            assert data["message"] == "Agent with ID 123 not found"
            assert data["status_code"] == 404
            assert data["details"]["agent_id"] == 123

            # Test session not found
            response = await client.get("/test-session-not-found")
            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "SESSION_NOT_FOUND"
            assert data["message"] == "Session with ID 456 not found"
            assert data["status_code"] == 404
            assert data["details"]["session_id"] == 456

    @pytest.mark.asyncio
    async def test_generic_exception_handler(self):
        """Test that generic exceptions are handled correctly"""
        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/test-generic-error")
        async def test_generic_error():
            raise ValueError("Something went wrong")

        transport = ASGITransport(app=app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test-generic-error")
            assert response.status_code == 500
            data = response.json()
            assert data["error"] == "INTERNAL_SERVER_ERROR"
            assert data["message"] == "An unexpected error occurred"
            assert data["status_code"] == 500
