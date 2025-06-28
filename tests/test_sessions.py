import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from app.dependencies import get_openai_client
from app.models.agent import Agent
from app.models.session import ChatSession


class TestSessions:
    """Test suite for session endpoints"""

    @pytest.mark.asyncio
    async def test_create_session(self, client: AsyncClient, sample_agent: Agent):
        """Test creating a new chat session"""
        response = await client.post(f"/api/v1/agents/{sample_agent.id}/sessions")
        assert response.status_code == 201
        data = response.json()
        assert data["agent_id"] == sample_agent.id
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_session_agent_not_found(self, client: AsyncClient):
        """Test creating session with non-existent agent"""
        response = await client.post("/api/v1/agents/999/sessions")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_sessions(self, client: AsyncClient, sample_agent: Agent):
        """Test listing sessions for an agent"""
        response = await client.get(f"/api/v1/agents/{sample_agent.id}/sessions")
        assert response.status_code == 200
        sessions = response.json()
        assert isinstance(sessions, list)

    @pytest.mark.asyncio
    async def test_list_sessions_pagination(self, client: AsyncClient, sample_agent: Agent):
        """Test session pagination"""
        response = await client.get(f"/api/v1/agents/{sample_agent.id}/sessions?skip=0&limit=5")
        assert response.status_code == 200
        sessions = response.json()
        assert isinstance(sessions, list)
        assert len(sessions) <= 5


class TestMessages:
    """Test suite for message endpoints"""

    @pytest.mark.asyncio
    async def test_send_message(
        self, client: AsyncClient, sample_session: ChatSession, mock_openai, app
    ):
        """Test sending a message and getting AI response"""

        # Override the OpenAI client dependency
        async def override_openai_client():
            return mock_openai.return_value

        app.dependency_overrides[get_openai_client] = override_openai_client

        try:
            message_data = {"content": "Hello, how are you?"}
            response = await client.post(
                f"/api/v1/sessions/{sample_session.id}/messages", json=message_data
            )
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert data["session_id"] == sample_session.id
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_send_message_session_not_found(self, client: AsyncClient, mock_openai):
        """Test sending message to non-existent session"""
        message_data = {"content": "Hello"}
        response = await client.post("/api/v1/sessions/999/messages", json=message_data)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_send_message_validation(self, client: AsyncClient, sample_session: ChatSession):
        """Test message validation"""
        # Test with empty content
        invalid_data = {"content": ""}
        response = await client.post(
            f"/api/v1/sessions/{sample_session.id}/messages", json=invalid_data
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_openai_error(
        self, client: AsyncClient, sample_session: ChatSession, app
    ):
        """Test handling OpenAI API errors"""

        # Override the OpenAI client dependency to raise an error
        async def override_openai_client():
            mock_client = AsyncMock()
            mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
            return mock_client

        app.dependency_overrides[get_openai_client] = override_openai_client

        try:
            message_data = {"content": "Hello"}
            response = await client.post(
                f"/api/v1/sessions/{sample_session.id}/messages", json=message_data
            )
            assert response.status_code == 500  # Should return 500 for OpenAI errors
            data = response.json()
            assert "Error generating response" in data["message"]
        finally:
            app.dependency_overrides.clear()
