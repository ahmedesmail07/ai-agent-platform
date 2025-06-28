"""
Factory module for creating and configuring the FastAPI application.

This module provides a factory function to create the FastAPI app with all
necessary middleware, routes, and configuration.
"""

import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.base import Base
from app.database.engine import engine
from app.exceptions import setup_exception_handlers
from app.routes import api_router


def create_app(
    title: str = "AI Agent Platform",
    description: str = "A FastAPI-based platform for AI agents",
    version: str = "1.0.0",
    debug: bool = False,
    cors_origins: Optional[List[str]] = None,
    static_files_dir: str = "audio_files",
    static_files_path: str = "/audio",
) -> FastAPI:
    """
    Create and configure a FastAPI application.

    Args:
        title: The title of the application
        description: The description of the application
        version: The version of the application
        debug: Whether to run in debug mode
        cors_origins: List of allowed CORS origins (defaults to ["*"])
        static_files_dir: Directory for static files
        static_files_path: URL path for static files

    Returns:
        Configured FastAPI application
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan manager."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        await engine.dispose()

    app = FastAPI(
        title=title,
        description=description,
        version=version,
        lifespan=lifespan,
        debug=debug,
    )

    setup_exception_handlers(app)

    if cors_origins is None:
        cors_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if os.path.exists(static_files_dir):
        app.mount(static_files_path, StaticFiles(directory=static_files_dir), name="audio")

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {"message": "Welcome to AI Agent Platform API"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


def create_test_app(
    title: str = "AI Agent Platform Test",
    description: str = "Test instance of AI Agent Platform",
    version: str = "1.0.0",
    cors_origins: Optional[List[str]] = None,
) -> FastAPI:
    """
    Create a FastAPI application configured for testing.

    Args:
        title: The title of the test application
        description: The description of the test application
        version: The version of the application
        cors_origins: List of allowed CORS origins (defaults to ["*"])

    Returns:
        Configured FastAPI application for testing
    """
    return create_app(
        title=title,
        description=description,
        version=version,
        debug=True,
        cors_origins=cors_origins or ["*"],
        static_files_dir="audio_files",
        static_files_path="/audio",
    )


def create_production_app(
    title: str = "AI Agent Platform",
    description: str = "Production instance of AI Agent Platform",
    version: str = "1.0.0",
    cors_origins: Optional[List[str]] = None,
) -> FastAPI:
    """
    Create a FastAPI application configured for production.

    Args:
        title: The title of the production application
        description: The description of the production application
        version: The version of the application
        cors_origins: List of allowed CORS origins (should be specific domains in production)

    Returns:
        Configured FastAPI application for production
    """
    if cors_origins is None:
        cors_origins = [
            # TODO: add the domains here for production
        ]

    return create_app(
        title=title,
        description=description,
        version=version,
        debug=False,
        cors_origins=cors_origins,
        static_files_dir="audio_files",
        static_files_path="/audio",
    )
