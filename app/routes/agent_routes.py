from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_agent_service
from app.database.engine import get_db
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.services.agent_service import AgentService

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
):
    """Create a new agent"""
    agent = await agent_service.create_agent(db, agent_data)
    return agent


@router.get("/", response_model=List[AgentResponse])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
):
    """Get all agents with pagination"""
    agents = await agent_service.get_agents(db, skip=skip, limit=limit)
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
):
    """Get agent by ID"""
    agent = await agent_service.get_agent(db, agent_id)
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
):
    """Update an agent"""
    agent = await agent_service.update_agent(db, agent_id, agent_data)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
):
    """Delete an agent"""
    await agent_service.delete_agent(db, agent_id)
    return None
