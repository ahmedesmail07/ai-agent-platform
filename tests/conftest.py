import asyncio
import os
from typing import AsyncGenerator, Generator, Optional
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db
from app.database.test_engine import TestAsyncSessionLocal, create_test_tables, drop_test_tables
from app.factory import create_test_app
from app.models.agent import Agent
from app.models.session import ChatSession, Message

TEST_DATABASE_URL: Optional[str] = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL environment variable is not set")

if "test" not in TEST_DATABASE_URL.lower() and "ai_agent_platform.db" in TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL should point to a test database, not production!")


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db_setup():
    """Setup test database tables."""
    await create_test_tables()
    yield
    await drop_test_tables()


@pytest_asyncio.fixture
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def app():
    """Create a test FastAPI application."""
    return create_test_app()


@pytest_asyncio.fixture
async def client(app, db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses."""
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_chat_response = AsyncMock()
        mock_chat_response.choices = [AsyncMock()]
        mock_chat_response.choices[0].message.content = "Hello! How can I help you today?"

        mock_speech_response = AsyncMock()
        mock_speech_response.stream_to_file = AsyncMock()

        mock_transcription_response = "Hello, this is a test transcription"

        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value=mock_chat_response
        )
        mock_client.return_value.audio.speech.create = AsyncMock(return_value=mock_speech_response)
        mock_client.return_value.audio.transcriptions.create = AsyncMock(
            return_value=mock_transcription_response
        )

        yield mock_client


@pytest_asyncio.fixture
async def sample_agent(db_session) -> Agent:
    """Create a sample agent for testing."""
    agent = Agent(
        name="Test Agent",
        description="A test agent for unit testing",
        agent_type="chatbot",
        is_active=True,
        configuration={
            "model": "gpt-3.5-turbo",
            "system_prompt": "You are a helpful test assistant.",
            "temperature": 0.7,
            "max_tokens": 1000,
        },
        capabilities={"text_generation": True, "conversation": True},
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def sample_session(db_session, sample_agent) -> ChatSession:
    """Create a sample chat session for testing."""
    session = ChatSession(agent_id=sample_agent.id)
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


@pytest_asyncio.fixture
async def sample_message(db_session, sample_session) -> Message:
    """Create a sample message for testing."""
    message = Message(
        session_id=sample_session.id,
        sender="user",
        content="Hello, this is a test message",
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message


@pytest.fixture
def sample_audio_file():
    """Create a sample audio file for testing."""
    import io

    wav_header = (
        b"RIFF"  # Chunk ID
        + (36).to_bytes(4, "little")  # Chunk size
        + b"WAVE"  # Format
        + b"fmt "  # Subchunk1 ID
        + (16).to_bytes(4, "little")  # Subchunk1 size
        + (1).to_bytes(2, "little")  # Audio format (PCM)
        + (1).to_bytes(2, "little")  # Number of channels
        + (44100).to_bytes(4, "little")  # Sample rate
        + (88200).to_bytes(4, "little")  # Byte rate
        + (2).to_bytes(2, "little")  # Block align
        + (16).to_bytes(2, "little")  # Bits per sample
        + b"data"  # Subchunk2 ID
        + (0).to_bytes(4, "little")  # Subchunk2 size
    )
    return io.BytesIO(wav_header)
