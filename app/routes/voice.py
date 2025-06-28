import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db
from app.exceptions import UnsupportedAudioFormatError
from app.schemas.voice import VoiceResponse
from app.dependencies import get_voice_service
from app.services.voice import VoiceService

router = APIRouter()


@router.post("/sessions/{session_id}/voice", response_model=VoiceResponse)
async def process_voice_message(
    session_id: int,
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    voice_service: VoiceService = Depends(get_voice_service),
):
    """Process voice message: speech-to-text -> AI response -> text-to-speech"""

    # Validate file type
    if not audio_file.filename:
        raise UnsupportedAudioFormatError("", message="No file provided")

    file_extension = Path(audio_file.filename).suffix.lower()
    if file_extension not in [".wav", ".mp3", ".m4a", ".webm"]:
        raise UnsupportedAudioFormatError(file_extension)

    # Create temporary file
    temp_file = None
    try:
        # Save uploaded file to temporary location
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        content = await audio_file.read()
        temp_file.write(content)
        temp_file.close()

        # Prepare audio metadata
        audio_metadata = {
            "original_filename": audio_file.filename,
            "file_size": len(content),
            "content_type": audio_file.content_type,
            "file_extension": file_extension,
        }

        # Process voice message
        user_msg, ai_msg, audio_response_path = await voice_service.process_voice_message(
            db, session_id, temp_file.name, audio_metadata
        )

        # Generate audio URL
        audio_filename = Path(audio_response_path).name
        audio_url = f"/audio/{audio_filename}"

        return VoiceResponse(
            message=str(ai_msg.content),
            session_id=session_id,
            audio_url=audio_url,
            transcription=str(user_msg.content),
        )

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


# @router.get("/audio/{audio_filename}")
# async def get_audio_file(audio_filename: str):
#     """Serve audio files"""
#     audio_path = await voice_service.get_audio_file_path(audio_filename)

#     if not audio_path:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")

#     return FileResponse(audio_path, media_type="audio/mpeg", filename=audio_filename)
