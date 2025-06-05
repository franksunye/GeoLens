"""
API v1 package initialization.
"""
from fastapi import APIRouter

from app.api.v1 import auth, projects, ai, mention_detection
# 暂时注释避免循环导入
# from app.api.v1 import mention_detection_unified

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

# 新的统一引用检测API - 暂时注释避免循环导入
# api_router.include_router(
#     mention_detection_unified.router,
#     tags=["mention-detection-unified"]
# )
