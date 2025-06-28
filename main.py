import os
import logging
import sys

import uvicorn
from dotenv import load_dotenv

from app.factory import create_app

# Import models to ensure they are registered with Base
# This import is necessary for table creation during startup
from app.models.agent import Agent  # noqa: F401
from app.models.audio import AudioMetadata  # noqa: F401
from app.models.session import ChatSession, Message  # noqa: F401

load_dotenv()


# Configure logging
def setup_logging():
    """Setup logging configuration for the application."""
    log_level = os.getenv("LOG_LEVEL", "info").upper()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(console_handler)

    # Configure specific loggers
    app_logger = logging.getLogger("app")
    app_logger.setLevel(getattr(logging, log_level))
    app_logger.addHandler(console_handler)

    # Configure exception handler logger specifically
    exception_logger = logging.getLogger("app.exceptions.handler")
    exception_logger.setLevel(getattr(logging, log_level))
    exception_logger.addHandler(console_handler)

    # Ensure SQLAlchemy logs are visible
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.INFO)
    sqlalchemy_logger.addHandler(console_handler)

    logging.info(f"Logging configured with level: {log_level}")


# Setup logging before creating the app
setup_logging()

app = create_app(
    title="AI Agent Platform",
    description="A FastAPI-based platform for AI agents",
    version="1.0.0",
    debug=True,
    cors_origins=["*"],
    static_files_dir="audio_files",
    static_files_path="/audio",
)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")
    reload = os.getenv("DEBUG", "False").lower() == "true"

    uvicorn.run("main:app", host=host, port=port, reload=reload, log_level=log_level)
