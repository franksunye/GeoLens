"""
AI服务抽象基类

定义AI服务的统一接口和数据结构。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import time


class AIRole(str, Enum):
    """AI对话角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class AIMessage:
    """AI消息数据结构"""
    role: AIRole
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """AI响应数据结构"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]  # token使用情况
    response_time: float  # 响应时间(秒)
    metadata: Optional[Dict[str, Any]] = None


class AIError(Exception):
    """AI服务异常基类"""
    
    def __init__(self, message: str, provider: str = None, error_code: str = None):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        super().__init__(message)


class AIProvider(ABC):
    """AI服务提供商抽象基类"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self._validate_config()
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """支持的模型列表"""
        pass
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置参数"""
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[AIMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> AIResponse:
        """
        聊天完成接口
        
        Args:
            messages: 对话消息列表
            model: 使用的模型名称
            temperature: 温度参数(0-1)
            max_tokens: 最大token数
            stream: 是否流式输出
            **kwargs: 其他参数
            
        Returns:
            AI响应结果
            
        Raises:
            AIError: AI服务异常
        """
        pass
    
    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[AIMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天完成接口
        
        Args:
            messages: 对话消息列表
            model: 使用的模型名称
            temperature: 温度参数(0-1)
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Yields:
            流式响应内容片段
            
        Raises:
            AIError: AI服务异常
        """
        pass
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            服务是否可用
        """
        try:
            test_messages = [
                AIMessage(role=AIRole.USER, content="Hello")
            ]
            await self.chat_completion(
                messages=test_messages,
                max_tokens=10
            )
            return True
        except Exception:
            return False
    
    def _create_response(
        self,
        content: str,
        model: str,
        usage: Dict[str, int],
        start_time: float,
        metadata: Dict[str, Any] = None
    ) -> AIResponse:
        """创建标准化响应"""
        return AIResponse(
            content=content,
            model=model,
            provider=self.provider_name,
            usage=usage,
            response_time=time.time() - start_time,
            metadata=metadata or {}
        )
