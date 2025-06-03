"""
AI服务依赖注入

提供AI服务的依赖注入和配置管理。
"""

from typing import Optional
from fastapi import Depends, HTTPException, status

from app.core.config import get_settings, Settings
from app.services.ai import AIServiceFactory, AIProvider, AIError


def get_ai_provider(
    provider_name: Optional[str] = None,
    settings: Settings = Depends(get_settings)
) -> AIProvider:
    """
    获取AI服务提供商实例
    
    Args:
        provider_name: 指定的提供商名称，如果为None则使用默认提供商
        settings: 应用设置
        
    Returns:
        AI服务提供商实例
        
    Raises:
        HTTPException: 当API密钥未配置或提供商不支持时
    """
    # 使用指定的提供商或默认提供商
    provider_name = provider_name or settings.default_ai_provider
    
    try:
        if provider_name == "doubao":
            if not settings.doubao_api_key:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Doubao API key not configured"
                )
            
            return AIServiceFactory.get_provider(
                provider_name="doubao",
                api_key=settings.doubao_api_key,
                base_url=settings.doubao_base_url,
                default_model=settings.doubao_default_model,
                timeout=settings.ai_request_timeout
            )
        
        elif provider_name == "deepseek":
            if not settings.deepseek_api_key:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="DeepSeek API key not configured"
                )
            
            return AIServiceFactory.get_provider(
                provider_name="deepseek",
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                default_model=settings.deepseek_default_model,
                timeout=settings.ai_request_timeout
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported AI provider: {provider_name}"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e.message}"
        )


def get_doubao_provider(
    settings: Settings = Depends(get_settings)
) -> AIProvider:
    """获取豆包AI服务提供商"""
    return get_ai_provider("doubao", settings)


def get_deepseek_provider(
    settings: Settings = Depends(get_settings)
) -> AIProvider:
    """获取DeepSeek AI服务提供商"""
    return get_ai_provider("deepseek", settings)


def get_default_ai_provider(
    settings: Settings = Depends(get_settings)
) -> AIProvider:
    """获取默认AI服务提供商"""
    return get_ai_provider(None, settings)
