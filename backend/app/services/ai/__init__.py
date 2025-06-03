"""
AI服务模块

提供统一的AI服务抽象层，支持多个AI平台的集成。
"""

from .base import AIProvider, AIResponse, AIMessage, AIError, AIRole
from .factory import AIServiceFactory
from .doubao import DoubaoProvider
from .deepseek import DeepSeekProvider

__all__ = [
    "AIProvider",
    "AIResponse", 
    "AIMessage",
    "AIError",
    "AIRole",
    "AIServiceFactory",
    "DoubaoProvider",
    "DeepSeekProvider",
]
