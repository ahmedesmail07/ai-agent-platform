from fastapi import APIRouter

from app.routes.agent_routes import router as agent_router
from app.routes.sessions import router as session_router
from app.routes.voice import router as voice_router

# Main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(agent_router, prefix="/agents", tags=["agents"])
api_router.include_router(session_router, tags=["sessions"])
api_router.include_router(voice_router, tags=["voice"])
