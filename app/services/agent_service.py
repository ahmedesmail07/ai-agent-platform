from typing import Sequence, List

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    AgentNotFoundError,
    AgentCreationError,
    AgentUpdateError,
    AgentDeletionError,
)
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    """Service for managing agents"""

    async def create_agent(self, db: AsyncSession, agent_data: AgentCreate) -> Agent:
        """Create a new agent"""
        try:
            agent = Agent(**agent_data.model_dump())
            db.add(agent)
            await db.commit()
            await db.refresh(agent)
            return agent
        except Exception as e:
            await db.rollback()
            raise AgentCreationError(
                message=f"Failed to create agent: {str(e)}",
                details={"agent_data": agent_data.model_dump()},
            )

    async def create_agents_bulk(
        self, db: AsyncSession, agents_data: List[AgentCreate]
    ) -> List[Agent]:
        """Create multiple agents in a single transaction"""
        try:
            agents = [Agent(**agent_data.model_dump()) for agent_data in agents_data]
            db.add_all(agents)
            await db.commit()

            # Refresh all agents to get their IDs
            for agent in agents:
                await db.refresh(agent)

            return agents
        except Exception as e:
            await db.rollback()
            raise AgentCreationError(
                message=f"Failed to create agents in bulk: {str(e)}",
                details={"agents_count": len(agents_data)},
            )

    async def get_agent(self, db: AsyncSession, agent_id: int) -> Agent:
        """Get agent by ID"""
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()

        if not agent:
            raise AgentNotFoundError(agent_id)

        return agent

    async def get_agents(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Agent]:
        """Get all agents with pagination"""
        result = await db.execute(select(Agent).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_agents_by_ids(self, db: AsyncSession, agent_ids: List[int]) -> List[Agent]:
        """Get multiple agents by their IDs"""
        if not agent_ids:
            return []

        result = await db.execute(select(Agent).where(Agent.id.in_(agent_ids)))
        return result.scalars().all()

    async def get_active_agents(self, db: AsyncSession) -> List[Agent]:
        """Get all active agents"""
        result = await db.execute(select(Agent).where(Agent.is_active))
        return result.scalars().all()

    async def update_agent(
        self, db: AsyncSession, agent_id: int, agent_data: AgentUpdate
    ) -> Agent:
        """Update an agent - optimized to use fewer queries"""
        # model_dump() is a method that converts the Pydantic model to a dictionary
        update_data = agent_data.model_dump(exclude_unset=True)
        if not update_data:
            # If no data to update, just return the existing agent
            return await self.get_agent(db, agent_id)

        try:
            # Use RETURNING clause to get the updated agent in a single query
            stmt = update(Agent).where(Agent.id == agent_id).values(**update_data).returning(Agent)
            result = await db.execute(stmt)
            updated_agent = result.scalar_one_or_none()

            if not updated_agent:
                raise AgentNotFoundError(agent_id)

            await db.commit()
            return updated_agent
        except AgentNotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            raise AgentUpdateError(agent_id, f"Failed to update agent: {str(e)}")

    async def update_agents_bulk(
        self, db: AsyncSession, updates: List[tuple[int, AgentUpdate]]
    ) -> List[Agent]:
        """Update multiple agents in a single transaction"""
        try:
            updated_agents = []
            for agent_id, agent_data in updates:
                update_data = agent_data.model_dump(exclude_unset=True)
                if update_data:
                    stmt = (
                        update(Agent)
                        .where(Agent.id == agent_id)
                        .values(**update_data)
                        .returning(Agent)
                    )
                    result = await db.execute(stmt)
                    agent = result.scalar_one_or_none()
                    if agent:
                        updated_agents.append(agent)

            await db.commit()
            return updated_agents
        except Exception as e:
            await db.rollback()
            raise AgentUpdateError(None, f"Failed to update agents in bulk: {str(e)}")

    async def delete_agent(self, db: AsyncSession, agent_id: int) -> bool:
        """Delete an agent - optimized to use fewer queries"""
        try:
            # Use RETURNING clause to check if agent existed and get confirmation
            stmt = delete(Agent).where(Agent.id == agent_id).returning(Agent.id)
            result = await db.execute(stmt)
            deleted_agent = result.scalar_one_or_none()

            if not deleted_agent:
                raise AgentNotFoundError(agent_id)

            await db.commit()
            return True
        except AgentNotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            raise AgentDeletionError(agent_id, f"Failed to delete agent: {str(e)}")

    async def delete_agents_bulk(self, db: AsyncSession, agent_ids: List[int]) -> int:
        """Delete multiple agents in a single transaction"""
        try:
            if not agent_ids:
                return 0

            stmt = delete(Agent).where(Agent.id.in_(agent_ids)).returning(Agent.id)
            result = await db.execute(stmt)
            deleted_count = len(result.scalars().all())

            await db.commit()
            return deleted_count
        except Exception as e:
            await db.rollback()
            raise AgentDeletionError(None, f"Failed to delete agents in bulk: {str(e)}")

    async def count_agents(self, db: AsyncSession) -> int:
        """Get total count of agents"""
        result = await db.execute(select(Agent.id))
        return len(result.scalars().all())

    async def count_active_agents(self, db: AsyncSession) -> int:
        """Get count of active agents"""
        result = await db.execute(select(Agent.id).where(Agent.is_active))
        return len(result.scalars().all())
