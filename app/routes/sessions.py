from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import get_db
from app.schemas.message import (
    AgentResponse,
    MessageResponse,
    UserMessageWithKnowledgeBase,
)
from app.schemas.session import ChatSessionResponse
from app.dependencies import get_session_service

from os import getenv
import json

import openai
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from app.services.session_service import SessionService
from app.models.agent import Agent

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
    message: UserMessageWithKnowledgeBase,
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
):
    """Send a user message and get AI response"""
    user_msg, ai_msg = await session_service.send_user_message_and_get_response(
        db, session_id, message.content, message.knowledge_base
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


@router.post("/sessions/{session_id}/summarize", response_model=AgentResponse)
async def summarize_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
):
    """Summarize all messages in a session using OpenAI"""
    summary = await session_service.summarize_session(db, session_id)
    return AgentResponse(message=summary, session_id=session_id)


@router.websocket("/ws/sessions/{session_id}")
async def websocket_session(
    websocket: WebSocket,
    session_id: int,
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
):
    """
    WebSocket endpoint for one-to-one chat streaming.
    Client must send JSON: {"content": "...", "knowledge_base": "..."}
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_content = payload.get("content")
            kb_override = payload.get("knowledge_base")

            await session_service.add_message(db, session_id, "user", user_content)

            session = await session_service.get_session(db, session_id)
            agent = await db.get(Agent, session.agent_id)

            messages = await session_service.get_session_messages(db, session_id)
            conv = []
            sys_p = agent.configuration.get("system_prompt", "") if agent.configuration else ""
            if sys_p:
                conv.append({"role": "system", "content": sys_p})
            for msg in messages:
                role = "user" if msg.sender == "user" else "assistant"
                conv.append({"role": role, "content": msg.content})
            conv.append({"role": "user", "content": user_content})
            final_kb = kb_override or (agent.configuration or {}).get("knowledge_base")
            if final_kb:
                conv.insert(
                    0,
                    {
                        "role": "system",
                        "content": f"This is important knowledge base context: {final_kb}",
                    },
                )

            client = session_service.openai_client or openai.AsyncOpenAI(
                api_key=getenv("OPENAI_API_KEY")
            )

            model = (agent.configuration or {}).get("model", session_service.default_model)
            max_toks = (agent.configuration or {}).get(
                "max_tokens", session_service.default_max_tokens
            )
            temp = (agent.configuration or {}).get(
                "temperature", session_service.default_temperature
            )

            stream = await client.chat.completions.create(
                model=model,
                messages=conv,  # type: ignore
                max_tokens=max_toks,
                temperature=temp,
                stream=True,
            )

            assistant_full = ""
            async for chunk in stream:
                delta = getattr(chunk.choices[0].delta, "content", None)
                if delta:
                    assistant_full += delta
                    await websocket.send_json({"sender": "agent", "content": delta})

            await session_service.add_message(db, session_id, "agent", assistant_full)

    except WebSocketDisconnect:
        return
    except Exception as err:
        await websocket.send_json({"error": str(err)})
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
