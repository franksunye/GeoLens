"""
内容分析API端点

提供网页爬取、内容分析和GEO评分功能。
"""

import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.deps import get_current_user
from app.models.user import User
# 临时简化的模式定义
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CrawlRequest(BaseModel):
    url: str
    timeout: Optional[int] = 30
    max_retries: Optional[int] = 3
    delay: Optional[float] = 1.0

class CrawlResponse(BaseModel):
    url: str
    status: str
    title: str
    content: str
    meta_description: str
    meta_keywords: List[str]
    headings: Dict[str, List[str]]
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    word_count: int
    reading_time: int
    language: Optional[str]
    schema_org: Dict[str, Any]
    crawl_time: datetime
    response_time: float

class AnalysisRequest(BaseModel):
    url: Optional[str] = None
    content: Optional[str] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    target_keywords: Optional[List[str]] = []
    brand_keywords: Optional[List[str]] = []

class AnalysisResponse(BaseModel):
    url: str
    content_analysis: Dict[str, Any]
    keyword_analysis: Dict[str, Any]
    entity_analysis: Dict[str, Any]
    extracted_content: Dict[str, Any]

class GEOScoreRequest(BaseModel):
    url: Optional[str] = None
    content: Optional[str] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    target_keywords: Optional[List[str]] = []
    brand_keywords: Optional[List[str]] = []
    previous_scores: Optional[List[Dict[str, Any]]] = []

class GEOScoreResponse(BaseModel):
    url: str
    geo_score: Dict[str, Any]
    analysis_summary: Dict[str, float]

class BatchAnalysisRequest(BaseModel):
    urls: List[str]
    target_keywords: Optional[List[str]] = []
    max_concurrent: Optional[int] = 3
    delay_between_requests: Optional[float] = 2.0

class BatchAnalysisResponse(BaseModel):
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    analysis_time: float
router = APIRouter()

# 初始化分析服务
from app.services.content_processing import ContentExtractor
from app.services.analysis import ContentAnalyzer, KeywordAnalyzer, GEOScorer, EntityExtractor

content_extractor = ContentExtractor()
content_analyzer = ContentAnalyzer()
keyword_analyzer = KeywordAnalyzer()
geo_scorer = GEOScorer()
entity_extractor = EntityExtractor()


@router.get("/health")
async def health_check():
    """
    健康检查

    检查GEO分析服务的可用性。
    """
    try:
        # 检查各个分析服务是否可用
        services_status = {
            "content_extractor": "healthy",
            "content_analyzer": "healthy",
            "keyword_analyzer": "healthy",
            "geo_scorer": "healthy",
            "entity_extractor": "healthy"
        }

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "services": services_status,
                "timestamp": "2024-06-03T12:00:00Z",
                "version": "3.0.0-sprint3-geo-focused"
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-06-03T12:00:00Z"
            }
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    GEO内容分析

    分析内容的AI友好度和GEO优化潜力。
    """
    try:
        # 处理内容输入
        if request.content:
            # 直接使用提供的内容
            content_text = request.content
        elif request.url:
            # 如果提供URL但没有内容，返回错误要求用户提供内容
            raise HTTPException(
                status_code=400,
                detail="Please provide content text for analysis. URL-only input is not supported in GEO-focused mode."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either content or URL must be provided"
            )

        # 使用ContentExtractor处理内容
        extracted_content = content_extractor.extract(content_text, request.url or "")
        if request.title:
            extracted_content.title = request.title
        if request.meta_description:
            extracted_content.meta_description = request.meta_description

        # 执行内容分析
        content_analysis = content_analyzer.analyze(
            extracted_content,
            request.target_keywords or []
        )

        # 执行关键词分析
        keyword_analysis = keyword_analyzer.analyze(
            extracted_content.main_content,
            extracted_content.title,
            extracted_content.meta_description,
            extracted_content.headings,
            request.target_keywords or []
        )

        # 执行实体提取
        entity_result = entity_extractor.extract(
            extracted_content.main_content,
            request.brand_keywords or []
        )

        return AnalysisResponse(
            url=request.url or "",
            content_analysis=content_analysis,
            keyword_analysis=keyword_analysis,
            entity_analysis=entity_result,
            extracted_content=extracted_content
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"GEO analysis failed: {str(e)}"
        )


@router.post("/geo-score", response_model=GEOScoreResponse)
async def calculate_geo_score(
    request: GEOScoreRequest,
    current_user: User = Depends(get_current_user)
):
    """
    计算GEO评分

    基于内容AI友好度计算生成式引擎优化评分。
    """
    try:
        # 首先进行内容分析
        analysis_request = AnalysisRequest(
            url=request.url,
            content=request.content,
            title=request.title,
            meta_description=request.meta_description,
            target_keywords=request.target_keywords,
            brand_keywords=request.brand_keywords
        )

        analysis_response = await analyze_content(analysis_request, current_user)

        # 计算GEO评分
        geo_score = geo_scorer.calculate_score(
            analysis_response.content_analysis,
            analysis_response.keyword_analysis,
            request.url or "",
            request.previous_scores or []
        )

        return GEOScoreResponse(
            url=request.url or "",
            geo_score=geo_score,
            analysis_summary={
                "content_quality": analysis_response.content_analysis.content_quality_score,
                "ai_friendliness": analysis_response.content_analysis.seo_analysis.overall_score(),
                "keyword_relevance": analysis_response.keyword_analysis.overall_keyword_score,
                "entity_count": analysis_response.entity_analysis.get_entity_count()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"GEO scoring failed: {str(e)}"
        )


# 健康检查端点已在上面定义
