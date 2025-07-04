import os
from typing import Dict, List, Optional, Sequence

import openai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app.exceptions import (
    SessionNotFoundError,
    SessionCreationError,
    AgentNotFoundError,
    MessageCreationError,
    InvalidSenderError,
    OpenAIChatCompletionError,
    OpenAIAPIError,
    OpenAIKeyError,
)
from app.models.agent import Agent
from app.models.session import ChatSession, Message


class SessionService:
    """Service for managing chat sessions and messages"""

    def __init__(
        self,
        default_model: str = "gpt-3.5-turbo",
        default_max_tokens: int = 1000,
        default_temperature: float = 0.7,
        openai_client: Optional[openai.AsyncOpenAI] = None,
    ):
        self.default_model = default_model
        self.default_max_tokens = default_max_tokens
        self.default_temperature = default_temperature
        self.openai_client = openai_client

    async def create_session(self, db: AsyncSession, agent_id: int) -> ChatSession:
        """Create a new chat session"""
        agent = await db.get(Agent, agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)

        try:
            session = ChatSession(agent_id=agent_id)
            db.add(session)
            await db.commit()
            await db.refresh(session)
            return session
        except Exception as e:
            await db.rollback()
            raise SessionCreationError(agent_id, f"Failed to create session: {str(e)}")

    async def get_sessions_by_agent(
        self, db: AsyncSession, agent_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[ChatSession]:
        """Get all sessions for an agent"""
        result = await db.execute(
            select(ChatSession).where(ChatSession.agent_id == agent_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_session(self, db: AsyncSession, session_id: int) -> ChatSession:
        """Get session by ID"""
        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = result.scalar_one_or_none()

        if not session:
            raise SessionNotFoundError(session_id)

        return session

    async def add_message(
        self, db: AsyncSession, session_id: int, sender: str, content: str
    ) -> Message:
        """Add a message to a session"""
        # Validate sender
        if sender not in ["user", "agent"]:
            raise InvalidSenderError(sender)

        try:
            message = Message(session_id=session_id, sender=sender, content=content)
            db.add(message)
            await db.commit()
            await db.refresh(message)
            return message
        except Exception as e:
            await db.rollback()
            raise MessageCreationError(session_id, f"Failed to create message: {str(e)}")

    async def get_session_messages(self, db: AsyncSession, session_id: int) -> Sequence[Message]:
        """Get all messages for a session"""
        # Verify session exists
        await self.get_session(db, session_id)

        result = await db.execute(
            select(Message)
            .options(selectinload(Message.audio_metadata))
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    async def send_user_message_and_get_response(
        self,
        db: AsyncSession,
        session_id: int,
        user_message: str,
        knowledge_base: Optional[str] = None,
    ) -> tuple[Message, Message]:
        """Send user message and get AI response"""
        session = await self.get_session(db, session_id)
        agent = await db.get(Agent, session.agent_id)
        if not agent:
            raise AgentNotFoundError(session.agent_id)

        user_msg = await self.add_message(db, session_id, "user", user_message)

        ai_response = await self._get_ai_response(
            db, session_id, user_message, agent, knowledge_base
        )

        ai_msg = await self.add_message(db, session_id, "agent", ai_response)

        return user_msg, ai_msg

    async def _get_ai_response(
        self,
        db: AsyncSession,
        session_id: int,
        user_message: str,
        agent: Agent,
        knowledge_base: Optional[str] = None,
    ) -> str:
        """Get AI response using OpenAI API"""
        messages = await self.get_session_messages(db, session_id)
        conversation: List[Dict[str, str]] = []
        system_prompt = agent.configuration.get("system_prompt", "") if agent.configuration else ""
        knowledge_base = (
            agent.configuration.get("knowledge_base", "") if agent.configuration else ""
        )
        if system_prompt:
            conversation.append({"role": "system", "content": system_prompt})

        for msg in messages:
            role = "user" if msg.sender == "user" else "assistant"
            msg_content = str(msg.content) if not isinstance(msg.content, str) else msg.content
            conversation.append({"role": role, "content": msg_content})

        conversation.append({"role": "user", "content": user_message})
        if knowledge_base:
            conversation.insert(
                0,
                {
                    "role": "system",
                    "content": f"This is important knowledge base context: {knowledge_base}",
                },
            )

        try:
            client = self.openai_client or openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            model = (
                agent.configuration.get("model", self.default_model)
                if agent.configuration
                else self.default_model
            )

            response = await client.chat.completions.create(
                model=model,
                messages=conversation,  # type: ignore
                max_tokens=(
                    agent.configuration.get("max_tokens", self.default_max_tokens)
                    if agent.configuration
                    else self.default_max_tokens
                ),
                temperature=(
                    agent.configuration.get("temperature", self.default_temperature)
                    if agent.configuration
                    else self.default_temperature
                ),
            )

            content: Optional[str] = response.choices[0].message.content
            if content is None:
                raise OpenAIChatCompletionError(
                    message="No response generated",
                    model=model,
                    messages_count=len(conversation),
                )
            return content

        except openai.AuthenticationError:
            raise OpenAIKeyError("Invalid OpenAI API key")
        except openai.APIError as e:
            raise OpenAIAPIError(
                message=f"OpenAI API error: {str(e)}",
                status_code=getattr(e, "status_code", None),
                api_response=getattr(e, "response", None),
            )
        except Exception as e:
            raise OpenAIChatCompletionError(
                message=f"Error generating response: {str(e)}",
                model=model,
                messages_count=len(conversation),
            )

    async def summarize_session(self, db: AsyncSession, session_id: int) -> str:
        """Generate a summary of the full session"""
        session = await self.get_session(db, session_id)
        agent = await db.get(Agent, session.agent_id)
        if not agent:
            raise AgentNotFoundError(session.agent_id)

        messages = await self.get_session_messages(db, session_id)

        # Build conversation text to summarize
        text = "\n".join([f"{msg.sender}: {msg.content}" for msg in messages])

        prompt = (
            "Summarize the following conversation between a user and an AI assistant:\n\n"
            + text
            + "\n\nSummary:"
        )

        try:
            client = self.openai_client or openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model = (
                agent.configuration.get("model", self.default_model)
                if agent.configuration
                else self.default_model
            )

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes conversations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.5,
            )

            content = response.choices[0].message.content
            return content if content else "No summary generated."

        except Exception as e:
            raise OpenAIChatCompletionError(
                message=f"Failed to summarize session: {str(e)}",
                model=model,
                messages_count=len(messages),
            )
