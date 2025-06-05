"""
API v1 package initialization.
"""
from fastapi import APIRouter

from app.api.v1 import auth, projects, ai, mention_detection

api_router = APIRouter()

# Include routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"]
)

api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["ai-services"]
)

api_router.include_router(
    mention_detection.router,
    prefix="/api",
    tags=["mention-detection"]
)
