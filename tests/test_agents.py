from app.models.agent import Agent

import pytest
from httpx import AsyncClient


class TestAgents:
    """Test suite for agent endpoints"""

    @pytest.mark.asyncio
    async def test_create_agent(self, client: AsyncClient):
        """Test creating a new agent"""
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "agent_type": "chatbot",
            "is_active": True,
            "configuration": {
                "model": "gpt-3.5-turbo",
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
            },
            "capabilities": {"text_generation": True, "conversation": True},
        }

        response = await client.post("/api/v1/agents/", json=agent_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == agent_data["name"]
        assert data["agent_type"] == agent_data["agent_type"]
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_agents(self, client: AsyncClient):
        """Test getting all agents"""
        response = await client.get("/api/v1/agents/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_agent_by_id(self, client: AsyncClient, sample_agent: Agent):
        """Test getting agent by ID"""
        response = await client.get(f"/api/v1/agents/{sample_agent.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_agent.id
        assert data["name"] == sample_agent.name
        assert isinstance(data["capabilities"], dict)

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, client: AsyncClient):
        """Test getting non-existent agent"""
        response = await client.get("/api/v1/agents/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_agent(self, client: AsyncClient, sample_agent: Agent):
        """Test updating an agent"""
        update_data = {
            "name": "Updated Agent Name",
            "description": "Updated description",
        }

        response = await client.put(f"/api/v1/agents/{sample_agent.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_delete_agent(self, client: AsyncClient, sample_agent: Agent):
        """Test deleting an agent"""
        response = await client.delete(f"/api/v1/agents/{sample_agent.id}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_create_agent_validation(self, client: AsyncClient):
        """Test agent creation validation"""
        invalid_data = {"description": "Missing name and type"}

        response = await client.post("/api/v1/agents/", json=invalid_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_agent_pagination(self, client: AsyncClient):
        """Test agent pagination"""
        response = await client.get("/api/v1/agents/?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for agent in data:
            assert isinstance(agent["capabilities"], dict)
        assert len(data) <= 5


class TestAgentServiceOptimizations:
    """Test suite for optimized agent service methods"""

    @pytest.mark.asyncio
    async def test_create_agents_bulk(self, db_session):
        """Test creating multiple agents in bulk"""
        from app.services.agent_service import AgentService
        from app.schemas.agent import AgentCreate

        service = AgentService()

        agents_data = [
            AgentCreate(
                name="Bulk Agent 1",
                description="First bulk agent",
                agent_type="chatbot",
                is_active=True,
                configuration={"model": "gpt-3.5-turbo"},
                capabilities={"text_generation": True},
            ),
            AgentCreate(
                name="Bulk Agent 2",
                description="Second bulk agent",
                agent_type="assistant",
                is_active=False,
                configuration={"model": "gpt-4"},
                capabilities={"conversation": True},
            ),
        ]

        agents = await service.create_agents_bulk(db_session, agents_data)
        assert len(agents) == 2
        assert agents[0].name == "Bulk Agent 1"
        assert agents[1].name == "Bulk Agent 2"
        assert agents[0].id is not None
        assert agents[1].id is not None

    @pytest.mark.asyncio
    async def test_get_agents_by_ids(self, db_session, sample_agent: Agent):
        """Test getting multiple agents by IDs"""
        from app.services.agent_service import AgentService

        service = AgentService()

        from app.schemas.agent import AgentCreate

        agent_data = AgentCreate(
            name="Second Agent",
            description="Another test agent",
            agent_type="assistant",
            is_active=True,
            configuration={"model": "gpt-4"},
            capabilities={"conversation": True},
        )
        second_agent = await service.create_agent(db_session, agent_data)

        agents = await service.get_agents_by_ids(db_session, [sample_agent.id, second_agent.id])
        assert len(agents) == 2
        agent_ids = [agent.id for agent in agents]
        assert sample_agent.id in agent_ids
        assert second_agent.id in agent_ids

    @pytest.mark.asyncio
    async def test_get_active_agents(self, db_session):
        """Test getting only active agents"""
        from app.services.agent_service import AgentService
        from app.schemas.agent import AgentCreate

        service = AgentService()

        active_agent_data = AgentCreate(
            name="Active Agent",
            description="An active agent",
            agent_type="chatbot",
            is_active=True,
            configuration={"model": "gpt-3.5-turbo"},
            capabilities={"text_generation": True},
        )

        inactive_agent_data = AgentCreate(
            name="Inactive Agent",
            description="An inactive agent",
            agent_type="assistant",
            is_active=False,
            configuration={"model": "gpt-4"},
            capabilities={"conversation": True},
        )

        await service.create_agent(db_session, active_agent_data)
        await service.create_agent(db_session, inactive_agent_data)

        active_agents = await service.get_active_agents(db_session)
        assert len(active_agents) >= 1
        for agent in active_agents:
            assert agent.is_active

    @pytest.mark.asyncio
    async def test_update_agent_optimized(self, db_session, sample_agent: Agent):
        """Test the optimized update method"""
        from app.services.agent_service import AgentService
        from app.schemas.agent import AgentUpdate

        service = AgentService()

        update_data = AgentUpdate(
            name="Optimized Update", description="Updated via optimized method"
        )
        updated_agent = await service.update_agent(db_session, sample_agent.id, update_data)

        assert updated_agent.name == "Optimized Update"
        assert updated_agent.description == "Updated via optimized method"
        assert updated_agent.id == sample_agent.id

    @pytest.mark.asyncio
    async def test_delete_agent_optimized(self, db_session, sample_agent: Agent):
        """Test the optimized delete method"""
        from app.services.agent_service import AgentService

        service = AgentService()

        result = await service.delete_agent(db_session, sample_agent.id)
        assert result

        with pytest.raises(Exception):
            await service.delete_agent(db_session, 99999)

    @pytest.mark.asyncio
    async def test_count_agents(self, db_session):
        """Test counting agents"""
        from app.services.agent_service import AgentService

        service = AgentService()

        total_count = await service.count_agents(db_session)
        active_count = await service.count_active_agents(db_session)

        assert total_count >= 0
        assert active_count >= 0
        assert active_count <= total_count
