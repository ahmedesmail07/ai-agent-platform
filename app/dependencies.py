"""
Dependency providers for services and shared resources.
"""

import os
from pathlib import Path
from functools import lru_cache

import openai
from fastapi import Depends

from app.services.agent_service import AgentService
from app.services.session_service import SessionService
from app.services.voice import VoiceService


@lru_cache()
def get_audio_dir() -> Path:
    """Provide the audio files directory as a Path object."""
    return Path(os.getenv("AUDIO_FILES_DIR", "audio_files"))


@lru_cache()
def get_openai_client() -> openai.AsyncOpenAI:
    """Provide a singleton OpenAI Async client."""
    return openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_agent_service(
    openai_client: openai.AsyncOpenAI = Depends(get_openai_client),
) -> AgentService:
    return AgentService()


def get_session_service(
    openai_client: openai.AsyncOpenAI = Depends(get_openai_client),
) -> SessionService:
    return SessionService(openai_client=openai_client)


def get_voice_service(
    audio_dir: Path = Depends(get_audio_dir),
    session_service: SessionService = Depends(get_session_service),
    openai_client: openai.AsyncOpenAI = Depends(get_openai_client),
) -> VoiceService:
    return VoiceService(
        audio_dir=audio_dir, session_service=session_service, openai_client=openai_client
    )
