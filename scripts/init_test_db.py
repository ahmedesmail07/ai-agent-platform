"""
Test Database Initialization Script

This script initializes a completely separate test database
to ensure isolation from the production database.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.database.test_engine import create_test_tables, drop_test_tables
    from app.exceptions.database import DatabaseMigrationError, DatabaseConnectionError
except ImportError:
    print(
        "ERROR: Could not import app module. "
        "Make sure you're running this from the project root."
    )
    sys.exit(1)


async def init_test_database():
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        print("TEST_DATABASE_URL is not set")
        return False

    if "ai_agent_platform.db" in test_db_url and "test" not in test_db_url.lower():
        print("Please use a separate test database file.")
        return False

    try:
        await drop_test_tables()
        await create_test_tables()
        return True

    except (DatabaseMigrationError, DatabaseConnectionError) as e:
        print(f"Database error: {e.message}")
        return False
    except Exception as e:
        print(f"Unexpected error initializing test database: {e}")
        return False


async def cleanup_test_database():
    try:
        await drop_test_tables()
        return True
    except (DatabaseMigrationError, DatabaseConnectionError) as e:
        print(f"Database error during cleanup: {e.message}")
        return False
    except Exception as e:
        print(f"Unexpected error cleaning up test database: {e}")
        return False


async def reset_test_database():
    try:
        await drop_test_tables()
        await create_test_tables()
        return True
    except (DatabaseMigrationError, DatabaseConnectionError) as e:
        print(f"Database error during reset: {e.message}")
        return False
    except Exception as e:
        print(f"Unexpected error resetting test database: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test Database Management")
    parser.add_argument(
        "action", choices=["init", "cleanup", "reset"], help="Action to perform on test database"
    )

    args = parser.parse_args()

    if args.action not in ["init", "cleanup", "reset"]:
        print("Invalid action. Please use one of the following: init, cleanup, reset")
        sys.exit(1)

    if args.action == "init":
        success = asyncio.run(init_test_database())
    elif args.action == "cleanup":
        success = asyncio.run(cleanup_test_database())
    elif args.action == "reset":
        success = asyncio.run(reset_test_database())

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
