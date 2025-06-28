import os
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError, TimeoutError as SQLAlchemyTimeoutError

from app.exceptions.database import DatabaseConnectionError, DatabaseTimeoutError
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

try:
    engine = create_async_engine(DATABASE_URL, echo=True, future=True)
    # echo in fast api is used to log the sql queries into the logs
except SQLAlchemyError as e:
    raise DatabaseConnectionError(
        message=f"Failed to create database engine: {str(e)}", database_url=DATABASE_URL
    )

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
# expire_on_commit is used to expire the session after the commit


async def get_db():
    """
    Dependency function that provides a database session.

    Yields:
        AsyncSession: An async SQLAlchemy session for database operations.

    The session is automatically closed when the request is complete.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyTimeoutError as e:
            raise DatabaseTimeoutError(
                message=f"Database operation timed out: {str(e)}",
                timeout_seconds=30,  # Default timeout
            )
        except SQLAlchemyError as e:
            raise DatabaseConnectionError(
                message=f"Database connection error: {str(e)}", database_url=DATABASE_URL
            )
        finally:
            await session.close()
