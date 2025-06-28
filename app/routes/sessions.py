from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db
from app.schemas.message import AgentResponse, MessageResponse, UserMessageCreate
from app.schemas.session import ChatSessionResponse
from app.dependencies import get_session_service
from app.services.session_service import SessionService

router = APIRouter()


@router.post(
    "/agents/{agent_id}/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
):
    """Start a new chat session with an agent"""
    session = await session_service.create_session(db, agent_id)
    return session


@router.get("/agents/{agent_id}/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    agent_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
):
    """List all sessions for an agent"""
    sessions = await session_service.get_sessions_by_agent(db, agent_id, skip=skip, limit=limit)
    return sessions


@router.post("/sessions/{session_id}/messages", response_model=AgentResponse)
async def send_message(
    session_id: int,
    message: UserMessageCreate,
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
):
    """Send a user message and get AI response"""
    user_msg, ai_msg = await session_service.send_user_message_and_get_response(
        db, session_id, message.content
    )
    return AgentResponse(message=str(ai_msg.content), session_id=session_id)


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
):
    """Get all messages for a session (user and agent)"""
    messages = await session_service.get_session_messages(db, session_id)
    return messages
