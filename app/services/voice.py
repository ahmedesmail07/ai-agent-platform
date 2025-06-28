import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

import openai
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    SpeechToTextError,
    TextToSpeechError,
    AudioMetadataError,
    VoiceServiceError,
    OpenAIAPIError,
    OpenAIKeyError,
    BaseDomainException,
)
from app.exceptions.database import DatabaseTransactionError
from app.models.audio import AudioMetadata
from app.models.session import Message
from app.services.session_service import SessionService


class VoiceService:
    """Service for handling voice interactions with AI agents"""

    def __init__(
        self,
        audio_dir: Path = Path("audio_files"),
        session_service: Optional[SessionService] = None,
        openai_key: Optional[str] = None,
        openai_client: Optional[openai.AsyncOpenAI] = None,
    ):
        self.audio_dir = audio_dir
        self.session_service = session_service or SessionService()
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        self.openai_client = openai_client or openai.AsyncOpenAI(api_key=self.openai_key)

    async def process_voice_message(
        self, db: AsyncSession, session_id: int, audio_file_path: str, audio_metadata: dict
    ) -> Tuple[Message, Message, str]:
        """
        Process voice message: speech-to-text -> AI response -> text-to-speech

        Returns: (user_message, ai_message, audio_response_path)
        """
        try:
            self.audio_dir.mkdir(exist_ok=True)

            user_text = await self._speech_to_text(audio_file_path)

            user_msg, ai_msg = await self.session_service.send_user_message_and_get_response(
                db, session_id, user_text
            )

            audio_response_path = await self._text_to_speech(str(ai_msg.content), session_id)

            await self._store_audio_metadata(
                db, int(user_msg.id), audio_metadata, audio_response_path, user_text
            )

            return user_msg, ai_msg, audio_response_path
        except (SpeechToTextError, TextToSpeechError, AudioMetadataError, BaseDomainException):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            raise VoiceServiceError(
                message=f"Voice processing failed: {str(e)}",
                session_id=session_id,
            )

    async def _speech_to_text(self, audio_file_path: str) -> str:
        """Convert audio file to text using OpenAI Whisper"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, response_format="text"
                )

            return transcript.strip()

        except openai.AuthenticationError:
            raise OpenAIKeyError("Invalid OpenAI API key for speech-to-text")
        except openai.APIError as e:
            raise OpenAIAPIError(
                message=f"OpenAI API error during speech-to-text: {str(e)}",
                status_code=getattr(e, "status_code", None),
                api_response=getattr(e, "response", None),
            )
        except Exception as e:
            raise SpeechToTextError(
                message=f"Speech-to-text conversion failed: {str(e)}",
                audio_file=audio_file_path,
                original_error=str(e),
            )

    async def _text_to_speech(self, text: str, session_id: int) -> str:
        """Convert text to speech using OpenAI TTS"""
        try:
            filename = f"response_{session_id}_{uuid.uuid4().hex}.mp3"
            output_path = self.audio_dir / filename

            response = await self.openai_client.audio.speech.create(
                model="tts-1", voice="alloy", input=text  # Can be configured per agent
            )

            response.stream_to_file(str(output_path))

            return str(output_path)

        except openai.AuthenticationError:
            raise OpenAIKeyError("Invalid OpenAI API key for text-to-speech")
        except openai.APIError as e:
            raise OpenAIAPIError(
                message=f"OpenAI API error during text-to-speech: {str(e)}",
                status_code=getattr(e, "status_code", None),
                api_response=getattr(e, "response", None),
            )
        except Exception as e:
            raise TextToSpeechError(
                message=f"Text-to-speech conversion failed: {str(e)}",
                text=text,
                original_error=str(e),
            )

    async def _store_audio_metadata(
        self,
        db: AsyncSession,
        message_id: int,
        audio_metadata: dict,
        response_audio_path: str,
        transcription_text: str,
    ) -> None:
        """Store audio metadata in the database so we can use it later"""
        try:
            metadata = AudioMetadata(
                message_id=message_id,
                input_audio_path=audio_metadata.get("original_filename"),
                output_audio_path=response_audio_path,
                input_audio_format=audio_metadata.get("file_extension"),
                output_audio_format="mp3",
                transcription_text=transcription_text,
                tts_voice="alloy",
                additional_metadata=audio_metadata,
            )

            db.add(metadata)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise AudioMetadataError(
                message=f"Failed to store audio metadata: {str(e)}",
                message_id=message_id,
            )
        except DatabaseTransactionError:
            raise

    async def get_audio_file_path(self, audio_filename: str) -> Optional[str]:
        """Get the full path to an audio file"""
        audio_path = self.audio_dir / audio_filename
        if audio_path.exists():
            return str(audio_path)
        return None

    async def cleanup_old_audio_files(self, max_age_hours: int = 24) -> int:
        """Clean up old audio files to save storage"""
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0

        for audio_file in self.audio_dir.glob("*.mp3"):
            if current_time - audio_file.stat().st_mtime > max_age_seconds:
                audio_file.unlink()
                deleted_count += 1

        return deleted_count
