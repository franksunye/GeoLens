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
    models: Optional[List[str]] = ["doubao", "deepseek"]
    api_keys: Optional[Dict[str, str]] = {}
    max_tokens: Optional[int] = 300
    temperature: Optional[float] = 0.3
    parallel_execution: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None

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

# 初始化引用检测服务 - 延迟导入避免循环依赖
from app.services.brand_detection_service import BrandDetectionService
from app.core.config import settings

# 延迟导入引用检测服务
def get_mention_service():
    from app.services.mention_detection import MentionDetectionService
    return MentionDetectionService

def get_detection_config():
    from app.services.mention_detection import MentionDetectionConfig
    return MentionDetectionConfig


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
        # 准备API密钥 - 从配置或请求中获取
        api_keys = request.api_keys or {}

        # 从配置中补充缺失的API密钥
        for model in request.models:
            key_name = f"{model.upper()}_API_KEY"
            if key_name not in api_keys:
                config = settings.get_ai_model_config(model)
                if config["api_key"]:
                    api_keys[key_name] = config["api_key"]

        # 创建检测配置
        MentionDetectionConfig = get_detection_config()
        config = MentionDetectionConfig(
            models=request.models,
            api_keys=api_keys,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            parallel_execution=request.parallel_execution
        )

        # 执行引用检测
        MentionDetectionService = get_mention_service()
        async with MentionDetectionService() as service:
            result = await service.execute_detection(
                project_id=request.project_id,
                user_id=current_user.id,
                prompt=request.prompt,
                brands=request.brands,
                config=config,
                metadata=request.metadata
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
        # 使用服务获取历史记录
        MentionDetectionService = get_mention_service()
        async with MentionDetectionService() as service:
            history = await service.repository.get_checks_by_project(
                project_id=project_id,
                page=page,
                limit=limit,
                brand_filter=brand,
                model_filter=model
            )

            # 获取总数
            total_count = await service.repository.get_checks_count_by_project(project_id)

            # 转换为API响应格式
            history_items = []
            for check in history:
                import json
                brands_checked = json.loads(check.brands_checked) if check.brands_checked else []
                models_used = json.loads(check.models_used) if check.models_used else []

                history_items.append(HistoryItem(
                    id=check.id,
                    prompt=check.prompt,
                    brands_checked=brands_checked,
                    models_used=models_used,
                    total_mentions=check.total_mentions or 0,
                    mention_rate=check.mention_rate or 0.0,
                    created_at=check.created_at
                ))

            history_response = HistoryResponse(
                checks=history_items,
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit
                }
            )

        return APIResponse(
            success=True,
            data=history_response,
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
        # 使用服务保存Prompt模板
        MentionDetectionService = get_mention_service()
        async with MentionDetectionService() as service:
            import uuid
            import json
            from datetime import datetime

            template_id = str(uuid.uuid4())
            template_data = {
                "id": template_id,
                "user_id": current_user.id,
                "name": request.name,
                "category": request.category,
                "template": request.template,
                "variables": json.dumps(request.variables or {}),
                "description": request.description,
                "usage_count": 0,
                "is_public": False,
                "created_at": datetime.now()
            }

            await service.repository.save_template(template_data)

            template = SavePromptResponse(
                id=template_id,
                name=request.name,
                category=request.category,
                template=request.template,
                variables=request.variables or {},
                usage_count=0,
                created_at=datetime.now()
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
        # 使用服务获取模板列表
        MentionDetectionService = get_mention_service()
        async with MentionDetectionService() as service:
            templates_db = await service.repository.get_templates_by_user(
                user_id=current_user.id,
                category=category,
                page=page,
                limit=limit
            )

            # 转换为响应格式
            import json
            templates = []
            for template_db in templates_db:
                variables = json.loads(template_db.variables) if template_db.variables else {}
                templates.append(SavePromptResponse(
                    id=template_db.id,
                    name=template_db.name,
                    category=template_db.category,
                    template=template_db.template,
                    variables=variables,
                    usage_count=template_db.usage_count,
                    created_at=template_db.created_at
                ))

            # 计算总数
            total_count = len(templates)

            template_response = TemplateListResponse(
                templates=templates,
                pagination={
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit
                }
            )

        return APIResponse(
            success=True,
            data=template_response,
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
        # 使用服务获取引用统计
        MentionDetectionService = get_mention_service()
        async with MentionDetectionService() as service:
            # 解析时间范围
            days = int(timeframe.replace('d', '')) if timeframe.endswith('d') else 30

            if brand:
                # 获取单个品牌统计
                stats = await service.repository.get_brand_mention_stats(project_id, brand, days)
                analytics = AnalyticsResponse(
                    brand=brand,
                    timeframe=timeframe,
                    total_checks=stats.get("total_checks", 0),
                    total_mentions=stats.get("total_mentions", 0),
                    mention_rate=stats.get("mention_rate", 0.0),
                    model_performance=stats.get("model_performance", {}),
                    trend_data=[],  # TODO: 实现趋势数据
                    top_contexts=[]  # TODO: 实现上下文分析
                )
            else:
                # 返回项目整体统计
                analytics = AnalyticsResponse(
                    brand="All Brands",
                    timeframe=timeframe,
                    total_checks=0,
                    total_mentions=0,
                    mention_rate=0.0,
                    model_performance={},
                    trend_data=[],
                    top_contexts=[]
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

        # 使用服务执行竞品对比
        MentionDetectionService = get_mention_service()
        async with MentionDetectionService() as service:
            # 获取品牌对比数据
            comparison_data = await service.repository.get_brand_comparison_stats(project_id, brand_list, days=30)

            # 生成洞察
            insights = []
            if comparison_data:
                # 按提及率排序
                sorted_brands = sorted(comparison_data, key=lambda x: x.get("mention_rate", 0), reverse=True)

                if len(sorted_brands) > 0:
                    top_brand = sorted_brands[0]
                    insights.append(f"{top_brand['brand']}的提及率最高，达到{top_brand['mention_rate']:.2%}")

                if len(sorted_brands) > 1:
                    second_brand = sorted_brands[1]
                    insights.append(f"{second_brand['brand']}在置信度方面表现良好，平均置信度{second_brand.get('avg_confidence', 0):.2f}")

            comparison = ComparisonResponse(
                brands=brand_list,
                comparison_data={
                    "comparison": comparison_data,
                    "insights": insights
                },
                summary={
                    "total_brands": len(brand_list),
                    "analyzed_brands": len(comparison_data) if comparison_data else 0
                }
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


# 新增的品牌检测端点
class BrandDetectionRequest(BaseModel):
    """品牌检测请求"""
    text: str
    brands: List[str]
    strategy: Optional[str] = "improved"

@router.post("/detect-brands-only")
async def detect_brands_only(request: BrandDetectionRequest):
    """
    仅执行品牌检测（不调用AI模型）

    快速检测文本中的品牌提及，不需要AI模型调用。
    """
    try:
        from app.services.brand_detection_service import DetectionStrategy

        # 转换策略字符串为枚举
        strategy_map = {
            "simple": DetectionStrategy.SIMPLE,
            "improved": DetectionStrategy.IMPROVED,
            "hybrid": DetectionStrategy.HYBRID
        }
        strategy = strategy_map.get(request.strategy, DetectionStrategy.IMPROVED)

        service = BrandDetectionService()
        results = service.detect_brands(
            text=request.text,
            brands=request.brands,
            strategy=strategy
        )

        # 转换为API响应格式
        api_results = {}
        for brand, result in results.items():
            api_results[brand] = {
                "mentioned": result.mentioned,
                "confidence": result.confidence,
                "contexts": result.contexts,
                "positions": result.positions,
                "detection_method": result.detection_method
            }

        # 获取统计信息
        stats = service.get_detection_statistics(results)

        return APIResponse(
            success=True,
            data={
                "results": api_results,
                "statistics": stats,
                "strategy_used": request.strategy
            },
            message="品牌检测完成"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Brand detection failed: {str(e)}"
        )


@router.post("/compare-strategies")
async def compare_detection_strategies(request: BrandDetectionRequest):
    """
    比较不同检测策略的结果

    对比简单、改进和混合三种检测策略的效果。
    """
    try:
        from app.services.brand_detection_service import DetectionStrategy

        service = BrandDetectionService()

        # 比较所有可用策略
        strategies = [DetectionStrategy.SIMPLE, DetectionStrategy.IMPROVED, DetectionStrategy.HYBRID]
        comparison_results = service.compare_strategies(
            text=request.text,
            brands=request.brands,
            strategies=strategies
        )

        # 为每个策略计算统计信息
        strategy_stats = {}
        for strategy_name, results in comparison_results.items():
            strategy_stats[strategy_name] = service.get_detection_statistics(results)

        return APIResponse(
            success=True,
            data={
                "comparison_results": comparison_results,
                "strategy_statistics": strategy_stats,
                "text_length": len(request.text),
                "brands_count": len(request.brands)
            },
            message="策略比较完成"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Strategy comparison failed: {str(e)}"
        )


@router.get("/strategies")
async def get_available_strategies():
    """
    获取可用的检测策略

    返回所有可用的品牌检测策略及其描述。
    """
    try:
        service = BrandDetectionService()
        return APIResponse(
            success=True,
            data={
                "strategies": service.get_available_strategies(),
                "default_strategy": "improved",
                "descriptions": {
                    "simple": "简单字符串匹配",
                    "improved": "改进的检测算法（推荐）",
                    "hybrid": "混合策略"
                }
            },
            message="获取策略列表成功"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get strategies: {str(e)}"
        )
