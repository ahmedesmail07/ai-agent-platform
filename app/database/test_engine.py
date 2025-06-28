import os
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.database import DatabaseConnectionError, DatabaseMigrationError

TEST_DATABASE_URL: Optional[str] = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL environment variable is not set")

try:
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
    )
except SQLAlchemyError as e:
    raise DatabaseConnectionError(
        message=f"Failed to create test database engine: {str(e)}", database_url=TEST_DATABASE_URL
    )

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


async def create_test_tables():
    """Create all tables in the test database"""
    from app.database.base import Base

    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except SQLAlchemyError as e:
        raise DatabaseMigrationError(
            message=f"Failed to create test tables: {str(e)}", migration_version="test_setup"
        )


async def drop_test_tables():
    """Drop all tables in the test database"""
    from app.database.base import Base

    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except SQLAlchemyError as e:
        raise DatabaseMigrationError(
            message=f"Failed to drop test tables: {str(e)}", migration_version="test_cleanup"
        )
