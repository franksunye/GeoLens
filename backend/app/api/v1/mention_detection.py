"""
引用检测API端点

提供品牌在生成式AI中的引用检测功能。
"""

import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from pydantic import BaseModel

# 引用检测相关的数据模型
class MentionCheckRequest(BaseModel):
    """引用检测请求"""
    project_id: str
    prompt: str
    brands: List[str]
    models: Optional[List[str]] = ["doubao", "deepseek", "chatgpt"]
    custom_template: Optional[bool] = False

class BrandMention(BaseModel):
    """品牌提及信息"""
    brand: str
    mentioned: bool
    confidence_score: float
    context_snippet: Optional[str] = None
    position: Optional[int] = None

class ModelResult(BaseModel):
    """单个模型的检测结果"""
    model: str
    response_text: str
    mentions: List[BrandMention]
    processing_time_ms: int

class MentionCheckResponse(BaseModel):
    """引用检测响应"""
    check_id: str
    project_id: str
    prompt: str
    status: str
    results: List[ModelResult]
    summary: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None

class HistoryRequest(BaseModel):
    """历史记录查询请求"""
    project_id: str
    page: Optional[int] = 1
    limit: Optional[int] = 20
    brand: Optional[str] = None
    model: Optional[str] = None

class HistoryItem(BaseModel):
    """历史记录项"""
    id: str
    prompt: str
    brands_checked: List[str]
    models_used: List[str]
    total_mentions: int
    mention_rate: float
    created_at: datetime

class HistoryResponse(BaseModel):
    """历史记录响应"""
    checks: List[HistoryItem]
    pagination: Dict[str, Any]

class PromptTemplate(BaseModel):
    """Prompt模板"""
    name: str
    category: str
    template: str
    variables: Optional[Dict[str, str]] = {}
    description: Optional[str] = None

class SavePromptRequest(BaseModel):
    """保存Prompt模板请求"""
    name: str
    category: str
    template: str
    variables: Optional[Dict[str, str]] = {}
    description: Optional[str] = None

class SavePromptResponse(BaseModel):
    """保存Prompt模板响应"""
    id: str
    name: str
    category: str
    template: str
    variables: Dict[str, str]
    usage_count: int
    created_at: datetime

class TemplateListResponse(BaseModel):
    """模板列表响应"""
    templates: List[SavePromptResponse]
    pagination: Dict[str, Any]

class AnalyticsResponse(BaseModel):
    """引用统计响应"""
    brand: str
    timeframe: str
    total_checks: int
    total_mentions: int
    mention_rate: float
    model_performance: Dict[str, Any]
    trend_data: List[Dict[str, Any]]
    top_contexts: List[str]

class ComparisonResponse(BaseModel):
    """品牌对比响应"""
    brands: List[str]
    comparison_data: Dict[str, Any]
    summary: Dict[str, Any]

router = APIRouter()

# 初始化引用检测服务
from app.services.mention_detection import MentionDetectionService

mention_service = MentionDetectionService()


@router.get("/health")
async def health_check():
    """
    健康检查
    
    检查引用检测服务的可用性。
    """
    try:
        # 检查各个服务是否可用
        services_status = {
            "mention_detection": "healthy",
            "ai_service": "healthy",
            "doubao_api": "healthy",
            "deepseek_api": "healthy",
            "openai_api": "healthy"
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "services": services_status,
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0-mention-detection"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@router.post("/check-mention", response_model=APIResponse[MentionCheckResponse])
async def check_mention(
    request: MentionCheckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    执行引用检测

    检测品牌在指定AI模型中的被提及情况。
    """
    try:
        # 执行引用检测
        result = await mention_service.check_mentions(
            prompt=request.prompt,
            brands=request.brands,
            models=request.models,
            project_id=request.project_id,
            user_id=current_user.id
        )

        return APIResponse(
            success=True,
            data=result,
            message="引用检测完成"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mention detection failed: {str(e)}"
        )


@router.get("/get-history", response_model=APIResponse[HistoryResponse])
async def get_history(
    project_id: str,
    page: int = 1,
    limit: int = 20,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取检测历史记录

    查询指定项目的历史检测记录。
    """
    try:
        # 获取历史记录
        history = await mention_service.get_history(
            project_id=project_id,
            page=page,
            limit=limit,
            brand_filter=brand,
            model_filter=model
        )

        return APIResponse(
            success=True,
            data=history,
            message="获取历史记录成功"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get history: {str(e)}"
        )


@router.post("/save-prompt", response_model=APIResponse[SavePromptResponse])
async def save_prompt(
    request: SavePromptRequest,
    current_user: User = Depends(get_current_user)
):
    """
    保存自定义Prompt模板

    保存用户自定义的Prompt模板供后续使用。
    """
    try:
        # 保存Prompt模板
        template = await mention_service.save_prompt_template(
            name=request.name,
            category=request.category,
            template=request.template,
            variables=request.variables or {},
            description=request.description,
            user_id=current_user.id
        )

        return APIResponse(
            success=True,
            data=template,
            message="Prompt模板保存成功"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save prompt template: {str(e)}"
        )


@router.get("/prompts/templates", response_model=APIResponse[TemplateListResponse])
async def get_prompt_templates(
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    获取Prompt模板列表

    获取可用的Prompt模板列表。
    """
    try:
        # 获取模板列表
        templates = await mention_service.get_prompt_templates(
            category=category,
            page=page,
            limit=limit,
            user_id=current_user.id
        )

        return APIResponse(
            success=True,
            data=templates,
            message="获取模板列表成功"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get prompt templates: {str(e)}"
        )


@router.get("/analytics/mentions", response_model=APIResponse[AnalyticsResponse])
async def get_mention_analytics(
    project_id: str,
    brand: Optional[str] = None,
    timeframe: str = "30d",
    model: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取品牌引用统计

    获取指定品牌的引用频率和趋势分析。
    """
    try:
        # 获取引用统计
        analytics = await mention_service.get_mention_analytics(
            project_id=project_id,
            brand=brand,
            timeframe=timeframe,
            model=model
        )

        return APIResponse(
            success=True,
            data=analytics,
            message="获取引用统计成功"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get mention analytics: {str(e)}"
        )


@router.get("/analytics/compare", response_model=APIResponse[ComparisonResponse])
async def compare_brands(
    project_id: str,
    brands: str,  # 逗号分隔的品牌列表
    current_user: User = Depends(get_current_user)
):
    """
    竞品对比分析

    对比多个品牌的AI可见性表现。
    """
    try:
        # 解析品牌列表
        brand_list = [brand.strip() for brand in brands.split(",")]

        # 执行竞品对比
        comparison = await mention_service.compare_brands(
            project_id=project_id,
            brands=brand_list
        )

        return APIResponse(
            success=True,
            data=comparison,
            message="品牌对比分析完成"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare brands: {str(e)}"
        )
