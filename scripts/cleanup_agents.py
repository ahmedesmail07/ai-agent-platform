"""
Agent Cleanup Script

This script removes all agents from the database.
Use with caution as this will permanently delete all agent data.
"""

import argparse
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import all models to ensure relationships are established
    from app.models.agent import Agent  # noqa: F401
    from app.models.session import ChatSession, Message  # noqa: F401
    from app.models.audio import AudioMetadata  # noqa: F401

    from app.database.engine import AsyncSessionLocal
    from app.services.agent_service import AgentService
    from app.exceptions import AgentDeletionError
except ImportError as e:
    print(
        "ERROR: Could not import app module. "
        "Make sure you're running this from the project root."
    )
    print(f"Import error: {e}")
    sys.exit(1)


async def cleanup_all_agents(dry_run: bool = False) -> bool:
    """
    Clean up all agents from the database.

    Args:
        dry_run: If True, only show what would be deleted without actually deleting

    Returns:
        bool: True if successful, False otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            agent_service = AgentService()

            # Get all agents first
            agents = await agent_service.get_agents(db, skip=0, limit=1000)

            if not agents:
                print("No agents found in the database.")
                return True

            print(f"Found {len(agents)} agents in the database:")
            for agent in agents:
                print(f"  - ID: {agent.id}, Name: '{agent.name}', Type: {agent.agent_type}")

            if dry_run:
                print(f"\nDRY RUN: Would delete {len(agents)} agents")
                return True

            # Confirm deletion
            confirm = input(
                f"\nAre you sure you want to delete all {len(agents)} agents? (yes/no): "
            )
            if confirm.lower() not in ["yes", "y"]:
                print("Operation cancelled.")
                return True

            # Get all agent IDs
            agent_ids = [agent.id for agent in agents]

            # Delete all agents in bulk
            deleted_count = await agent_service.delete_agents_bulk(db, agent_ids)

            print(f"Successfully deleted {deleted_count} agents.")
            return True

        except AgentDeletionError as e:
            print(f"Error deleting agents: {e.message}")
            return False
        except Exception as e:
            print(f"Unexpected error during cleanup: {e}")
            return False


async def cleanup_agents_by_type(agent_type: str, dry_run: bool = False) -> bool:
    """
    Clean up agents by type.

    Args:
        agent_type: The type of agents to delete
        dry_run: If True, only show what would be deleted without actually deleting

    Returns:
        bool: True if successful, False otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            agent_service = AgentService()

            # Get all agents first
            agents = await agent_service.get_agents(db, skip=0, limit=1000)

            # Filter by type
            filtered_agents = [agent for agent in agents if agent.agent_type == agent_type]

            if not filtered_agents:
                print(f"No agents found with type '{agent_type}'.")
                return True

            print(f"Found {len(filtered_agents)} agents with type '{agent_type}':")
            for agent in filtered_agents:
                print(f"  - ID: {agent.id}, Name: '{agent.name}'")

            if dry_run:
                print(
                    f"\nDRY RUN: Would delete {len(filtered_agents)} agents of type '{agent_type}'"
                )
                return True

            # Confirm deletion
            confirm_msg = (
                f"\nAre you sure you want to delete all {len(filtered_agents)} "
                f"agents of type '{agent_type}'? (yes/no): "
            )
            confirm = input(confirm_msg)
            if confirm.lower() not in ["yes", "y"]:
                print("Operation cancelled.")
                return True

            # Get agent IDs
            agent_ids = [agent.id for agent in filtered_agents]

            # Delete agents in bulk
            deleted_count = await agent_service.delete_agents_bulk(db, agent_ids)

            print(f"Successfully deleted {deleted_count} agents of type '{agent_type}'.")
            return True

        except AgentDeletionError as e:
            print(f"Error deleting agents: {e.message}")
            return False
        except Exception as e:
            print(f"Unexpected error during cleanup: {e}")
            return False


async def list_agents() -> bool:
    """
    List all agents in the database.

    Returns:
        bool: True if successful, False otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            agent_service = AgentService()

            # Get all agents
            agents = await agent_service.get_agents(db, skip=0, limit=1000)

            if not agents:
                print("No agents found in the database.")
                return True

            print(f"Found {len(agents)} agents in the database:")
            print("-" * 80)

            for agent in agents:
                print(f"ID: {agent.id}")
                print(f"Name: {agent.name}")
                print(f"Type: {agent.agent_type}")
                print(f"Active: {agent.is_active}")
                print(f"Description: {agent.description or 'N/A'}")
                if agent.configuration:
                    print(f"Configuration: {agent.configuration}")
                if agent.capabilities:
                    print(f"Capabilities: {agent.capabilities}")
                print("-" * 80)

            return True

        except Exception as e:
            print(f"Error listing agents: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Agent Cleanup Tool")
    parser.add_argument(
        "action", choices=["list", "cleanup-all", "cleanup-type"], help="Action to perform"
    )
    parser.add_argument("--type", help="Agent type to delete (required for cleanup-type action)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )

    args = parser.parse_args()

    if args.action == "cleanup-type" and not args.type:
        print("ERROR: --type argument is required for cleanup-type action")
        sys.exit(1)

    if args.action == "list":
        success = asyncio.run(list_agents())
    elif args.action == "cleanup-all":
        success = asyncio.run(cleanup_all_agents(dry_run=args.dry_run))
    elif args.action == "cleanup-type":
        success = asyncio.run(cleanup_agents_by_type(args.type, dry_run=args.dry_run))
    else:
        print("Invalid action. Please use one of the following: list, cleanup-all, cleanup-type")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
