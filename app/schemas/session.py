from datetime import datetime
from typing import List

from pydantic import BaseModel

from .message import MessageResponse


class ChatSessionBase(BaseModel):
    """Base ChatSession schema"""

    pass


class ChatSessionResponse(ChatSessionBase):
    """Schema for chat session response"""

    id: int
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    """Schema for chat session with messages"""

    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
