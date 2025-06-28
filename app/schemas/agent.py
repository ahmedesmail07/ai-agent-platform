from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Base Agent schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    agent_type: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True
    configuration: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None


class AgentCreate(AgentBase):
    """Schema for creating an agent"""

    pass


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    agent_type: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    """Schema for agent response"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        # automagically convert the model to a dictionary
        from_attributes = True
