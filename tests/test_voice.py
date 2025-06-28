import io
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.dependencies import get_openai_client
from app.models.session import ChatSession


class TestVoice:
    """Test suite for voice endpoints"""

    @pytest.mark.asyncio
    async def test_voice_message_processing(
        self, client: AsyncClient, sample_session: ChatSession, mock_openai, app
    ):
        """Test processing voice message end-to-end"""
        # Override the OpenAI client dependency
        async def override_openai_client():
            return mock_openai.return_value

        app.dependency_overrides[get_openai_client] = override_openai_client

        try:
            # Create a sample audio file
            audio_file = io.BytesIO(b"fake audio data")

            response = await client.post(
                f"/api/v1/sessions/{sample_session.id}/voice",
                files={"audio_file": ("test.wav", audio_file, "audio/wav")},
            )

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "audio_url" in data
            assert "transcription" in data
            assert data["session_id"] == sample_session.id
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_voice_message_validation(
        self, client: AsyncClient, sample_session: ChatSession
    ):
        """Test voice message validation"""
        # Test with invalid file type
        invalid_file = io.BytesIO(b"not an audio file")
        response = await client.post(
            f"/api/v1/sessions/{sample_session.id}/voice",
            files={"audio_file": ("test.txt", invalid_file, "text/plain")},
        )
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported audio format" in data["message"]

    @pytest.mark.asyncio
    async def test_voice_message_no_file(self, client: AsyncClient, sample_session: ChatSession):
        """Test voice message without file"""
        response = await client.post(f"/api/v1/sessions/{sample_session.id}/voice")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_voice_message_session_not_found(
        self, client: AsyncClient, sample_audio_file, app
    ):
        """Test voice message with non-existent session"""
        # Override the OpenAI client dependency
        async def override_openai_client():
            mock_client = AsyncMock()
            mock_client.audio.transcriptions.create = AsyncMock(return_value="Test transcription")
            mock_client.audio.speech.create = AsyncMock(return_value=AsyncMock())
            return mock_client

        app.dependency_overrides[get_openai_client] = override_openai_client

        try:
            response = await client.post(
                "/api/v1/sessions/999/voice",
                files={"audio_file": ("test.wav", sample_audio_file, "audio/wav")},
            )
            assert response.status_code == 404  # Should return 404 for non-existent session
            data = response.json()
            assert "Session with ID 999 not found" in data["message"]
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_voice_message_openai_error(
        self, client: AsyncClient, sample_session: ChatSession, app
    ):
        """Test handling OpenAI API errors in voice processing"""
        # Override the OpenAI client dependency to raise an error
        async def override_openai_client():
            mock_client = AsyncMock()
            mock_client.audio.transcriptions.create.side_effect = Exception("OpenAI API Error")
            return mock_client

        app.dependency_overrides[get_openai_client] = override_openai_client

        try:
            audio_file = io.BytesIO(b"fake audio data")
            response = await client.post(
                f"/api/v1/sessions/{sample_session.id}/voice",
                files={"audio_file": ("test.wav", audio_file, "audio/wav")},
            )
            assert response.status_code == 500  # Should return 500 for OpenAI errors
            data = response.json()
            assert "Speech-to-text conversion failed" in data["message"]
        finally:
            app.dependency_overrides.clear()


class TestAudioFiles:
    """Test suite for audio file serving"""

    @pytest.mark.asyncio
    async def test_get_audio_file_not_found(self, client: AsyncClient):
        """Test serving non-existent audio file"""
        response = await client.get("/audio/nonexistent.mp3")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_audio_file_success(self, client: AsyncClient):
        """Test serving existing audio file"""
        audio_dir = Path("audio_files")
        audio_dir.mkdir(exist_ok=True)

        test_audio = b"fake audio data"
        test_filename = "test_response.mp3"
        test_path = audio_dir / test_filename

        try:
            test_path.write_bytes(test_audio)

            response = await client.get(f"/audio/{test_filename}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/mpeg"

        finally:
            if test_path.exists():
                test_path.unlink()
