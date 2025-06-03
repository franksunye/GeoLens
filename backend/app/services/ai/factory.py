"""
AI服务工厂类

负责创建和管理不同的AI服务提供商实例。
"""

from typing import Dict, Type, Optional
from .base import AIProvider


class AIServiceFactory:
    """AI服务工厂"""
    
    _providers: Dict[str, Type[AIProvider]] = {}
    _instances: Dict[str, AIProvider] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIProvider]) -> None:
        """
        注册AI服务提供商
        
        Args:
            name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        api_key: str,
        **kwargs
    ) -> AIProvider:
        """
        创建AI服务提供商实例
        
        Args:
            provider_name: 提供商名称 (doubao, deepseek)
            api_key: API密钥
            **kwargs: 其他配置参数
            
        Returns:
            AI服务提供商实例
            
        Raises:
            ValueError: 不支持的提供商
        """
        if provider_name not in cls._providers:
            raise ValueError(
                f"Unsupported AI provider: {provider_name}. "
                f"Supported providers: {list(cls._providers.keys())}"
            )
        
        provider_class = cls._providers[provider_name]
        return provider_class(api_key=api_key, **kwargs)
    
    @classmethod
    def get_provider(
        cls,
        provider_name: str,
        api_key: str = None,
        **kwargs
    ) -> AIProvider:
        """
        获取AI服务提供商实例(单例模式)
        
        Args:
            provider_name: 提供商名称
            api_key: API密钥(首次创建时需要)
            **kwargs: 其他配置参数
            
        Returns:
            AI服务提供商实例
        """
        if provider_name not in cls._instances:
            if not api_key:
                raise ValueError(f"API key required for first-time creation of {provider_name}")
            cls._instances[provider_name] = cls.create_provider(
                provider_name, api_key, **kwargs
            )
        
        return cls._instances[provider_name]
    
    @classmethod
    def list_providers(cls) -> list[str]:
        """获取支持的提供商列表"""
        return list(cls._providers.keys())
    
    @classmethod
    def clear_instances(cls) -> None:
        """清除所有实例(主要用于测试)"""
        cls._instances.clear()


# 延迟导入以避免循环依赖
def _register_default_providers():
    """注册默认的AI服务提供商"""
    try:
        from .doubao import DoubaoProvider
        AIServiceFactory.register_provider("doubao", DoubaoProvider)
    except ImportError:
        pass
    
    try:
        from .deepseek import DeepSeekProvider
        AIServiceFactory.register_provider("deepseek", DeepSeekProvider)
    except ImportError:
        pass


# 自动注册默认提供商
_register_default_providers()
