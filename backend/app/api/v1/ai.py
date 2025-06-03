"""
AI服务API路由

提供AI聊天、品牌分析等功能的API端点。
"""

import asyncio
import time
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.ai_deps import get_ai_provider, get_default_ai_provider
from app.core.config import get_settings, Settings
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.ai import (
    ChatRequest, ChatResponse, AIProvidersResponse, AIProviderInfo,
    BrandAnalysisRequest, BrandAnalysisResponse, AIProviderEnum
)
from app.services.ai import AIProvider, AIMessage, AIRole, AIError, AIServiceFactory


router = APIRouter()


@router.get("/providers", response_model=AIProvidersResponse)
async def get_ai_providers(
    settings: Settings = Depends(get_settings)
) -> AIProvidersResponse:
    """
    获取可用的AI服务提供商列表
    """
    providers = []
    
    # 豆包提供商信息
    doubao_available = bool(settings.doubao_api_key)
    providers.append(AIProviderInfo(
        name="doubao",
        display_name="豆包(火山引擎)",
        supported_models=[
            "doubao-pro-32k", "doubao-pro-256k", "doubao-lite-32k",
            "doubao-lite-128k", "doubao-lite-4k", "doubao-vision-pro",
            "doubao-vision-lite", "doubao-1.5-pro-32k", "doubao-1.5-lite"
        ],
        available=doubao_available,
        description="字节跳动旗下的大语言模型服务，支持多种场景的智能对话"
    ))
    
    # DeepSeek提供商信息
    deepseek_available = bool(settings.deepseek_api_key)
    providers.append(AIProviderInfo(
        name="deepseek",
        display_name="DeepSeek",
        supported_models=["deepseek-chat", "deepseek-reasoner"],
        available=deepseek_available,
        description="DeepSeek AI的大语言模型服务，擅长推理和代码生成"
    ))
    
    return AIProvidersResponse(
        providers=providers,
        default_provider=settings.default_ai_provider
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
) -> ChatResponse:
    """
    AI聊天完成接口
    """
    try:
        # 获取AI服务提供商
        if request.provider:
            ai_provider = get_ai_provider(request.provider.value, settings)
        else:
            ai_provider = get_default_ai_provider(settings)
        
        # 转换消息格式
        messages = [
            AIMessage(
                role=AIRole(msg.role.value),
                content=msg.content
            )
            for msg in request.messages
        ]
        
        # 调用AI服务
        response = await ai_provider.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        return ChatResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            usage={
                "prompt_tokens": response.usage["prompt_tokens"],
                "completion_tokens": response.usage["completion_tokens"],
                "total_tokens": response.usage["total_tokens"]
            },
            response_time=response.response_time,
            metadata=response.metadata
        )
        
    except AIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_completion_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    AI流式聊天完成接口
    """
    try:
        # 获取AI服务提供商
        if request.provider:
            ai_provider = get_ai_provider(request.provider.value, settings)
        else:
            ai_provider = get_default_ai_provider(settings)
        
        # 转换消息格式
        messages = [
            AIMessage(
                role=AIRole(msg.role.value),
                content=msg.content
            )
            for msg in request.messages
        ]
        
        async def generate_stream():
            """生成流式响应"""
            try:
                async for chunk in ai_provider.chat_completion_stream(
                    messages=messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except AIError as e:
                yield f"data: {{\"error\": \"{e.message}\"}}\n\n"
            except Exception as e:
                yield f"data: {{\"error\": \"Unexpected error: {str(e)}\"}}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/analyze/brand", response_model=BrandAnalysisResponse)
async def analyze_brand_mentions(
    request: BrandAnalysisRequest,
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
) -> BrandAnalysisResponse:
    """
    品牌提及分析接口
    """
    start_time = time.time()
    
    try:
        # 获取AI服务提供商
        if request.provider:
            ai_provider = get_ai_provider(request.provider.value, settings)
        else:
            ai_provider = get_default_ai_provider(settings)
        
        # 构建分析提示词
        keywords_str = "、".join(request.brand_keywords)
        system_prompt = f"""你是一个专业的品牌监测分析师。请分析给定内容中关于品牌关键词"{keywords_str}"的提及情况。

请按照以下JSON格式返回分析结果：
{{
    "mentions": [
        {{
            "keyword": "关键词",
            "count": 提及次数,
            "context": ["上下文1", "上下文2"],
            "sentiment": "positive/negative/neutral",
            "confidence": 0.0-1.0
        }}
    ],
    "total_mentions": 总提及次数,
    "overall_sentiment": "positive/negative/neutral",
    "analysis_summary": "分析摘要"
}}

要求：
1. 准确识别所有品牌关键词的提及
2. 分析每个提及的情感倾向
3. 提供相关的上下文信息
4. 给出整体的情感评估
"""
        
        user_prompt = f"请分析以下内容：\n\n{request.content}"
        
        messages = [
            AIMessage(role=AIRole.SYSTEM, content=system_prompt),
            AIMessage(role=AIRole.USER, content=user_prompt)
        ]
        
        # 调用AI服务
        response = await ai_provider.chat_completion(
            messages=messages,
            temperature=0.3,  # 使用较低的温度以获得更一致的结果
            max_tokens=2000
        )
        
        # 解析AI响应 (这里简化处理，实际应该解析JSON)
        # TODO: 实现更完善的JSON解析和错误处理
        
        # 临时返回示例数据
        processing_time = time.time() - start_time
        
        return BrandAnalysisResponse(
            mentions=[],  # TODO: 解析AI响应中的提及信息
            total_mentions=0,
            overall_sentiment="neutral",
            analysis_summary=response.content[:200] + "...",
            provider=response.provider,
            processing_time=processing_time
        )
        
    except AIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/health")
async def health_check(
    provider: str = None,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    AI服务健康检查
    """
    results = {}
    
    providers_to_check = [provider] if provider else ["doubao", "deepseek"]
    
    for provider_name in providers_to_check:
        try:
            ai_provider = get_ai_provider(provider_name, settings)
            is_healthy = await ai_provider.health_check()
            results[provider_name] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "available": True
            }
        except HTTPException as e:
            results[provider_name] = {
                "status": "unavailable",
                "available": False,
                "error": e.detail
            }
        except Exception as e:
            results[provider_name] = {
                "status": "error",
                "available": False,
                "error": str(e)
            }
    
    return {
        "providers": results,
        "timestamp": time.time()
    }
