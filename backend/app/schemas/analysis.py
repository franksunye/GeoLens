"""
内容分析相关的Pydantic模式定义
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator


# 爬虫相关模式
class CrawlRequest(BaseModel):
    """爬取请求"""
    url: str = Field(..., description="目标URL")
    timeout: Optional[int] = Field(30, description="超时时间(秒)")
    max_retries: Optional[int] = Field(3, description="最大重试次数")
    delay: Optional[float] = Field(1.0, description="请求延迟(秒)")
    
    @validator("url")
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class CrawlResponse(BaseModel):
    """爬取响应"""
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


# 分析相关模式
class AnalysisRequest(BaseModel):
    """分析请求"""
    url: Optional[str] = Field(None, description="要分析的URL")
    content: Optional[str] = Field(None, description="直接提供的内容")
    title: Optional[str] = Field(None, description="页面标题")
    meta_description: Optional[str] = Field(None, description="Meta描述")
    target_keywords: Optional[List[str]] = Field([], description="目标关键词")
    brand_keywords: Optional[List[str]] = Field([], description="品牌关键词")
    
    @validator("content", "url")
    def validate_content_or_url(cls, v, values):
        if not v and not values.get("url"):
            raise ValueError("Either content or url must be provided")
        return v


class SEOAnalysisResponse(BaseModel):
    """SEO分析响应"""
    title_length: int
    title_score: float
    meta_description_length: int
    meta_description_score: float
    heading_structure_score: float
    keyword_density: Dict[str, float]
    internal_links_count: int
    external_links_count: int
    images_without_alt: int
    schema_org_present: bool
    overall_score: float


class ReadabilityAnalysisResponse(BaseModel):
    """可读性分析响应"""
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_words_per_sentence: float
    avg_sentences_per_paragraph: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    readability_score: float
    reading_level: str


class StructureAnalysisResponse(BaseModel):
    """结构分析响应"""
    heading_hierarchy: Dict[str, int]
    heading_structure_issues: List[str]
    content_sections: int
    list_count: int
    table_count: int
    structure_score: float


class ContentAnalysisResponse(BaseModel):
    """内容分析响应"""
    url: str
    seo_analysis: SEOAnalysisResponse
    readability_analysis: ReadabilityAnalysisResponse
    structure_analysis: StructureAnalysisResponse
    content_quality_score: float
    recommendations: List[str]
    overall_score: float


class KeywordMetricsResponse(BaseModel):
    """关键词指标响应"""
    keyword: str
    frequency: int
    density: float
    prominence_score: float
    positions: List[int]
    context_relevance: float


class KeywordAnalysisResponse(BaseModel):
    """关键词分析响应"""
    target_keywords: List[KeywordMetricsResponse]
    discovered_keywords: List[KeywordMetricsResponse]
    keyword_clusters: Dict[str, List[str]]
    semantic_keywords: List[str]
    keyword_stuffing_risk: float
    overall_keyword_score: float


class EntityResponse(BaseModel):
    """实体响应"""
    text: str
    entity_type: str
    confidence: float
    positions: List[int]
    context: List[str]


class EntityAnalysisResponse(BaseModel):
    """实体分析响应"""
    persons: List[EntityResponse]
    organizations: List[EntityResponse]
    locations: List[EntityResponse]
    brands: List[EntityResponse]
    products: List[EntityResponse]
    technologies: List[EntityResponse]
    other: List[EntityResponse]
    total_entities: int


class ExtractedContentResponse(BaseModel):
    """提取内容响应"""
    title: str
    main_content: str
    meta_description: str
    meta_keywords: List[str]
    headings: Dict[str, List[str]]
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    schema_org: Dict[str, Any]
    word_count: int
    reading_time: int
    language: Optional[str]
    author: Optional[str]
    publish_date: Optional[str]


class AnalysisResponse(BaseModel):
    """综合分析响应"""
    url: str
    content_analysis: ContentAnalysisResponse
    keyword_analysis: KeywordAnalysisResponse
    entity_analysis: EntityAnalysisResponse
    extracted_content: ExtractedContentResponse


# GEO评分相关模式
class GEOFactorsResponse(BaseModel):
    """GEO评分因子响应"""
    content_quality: float
    content_length: float
    readability: float
    originality: float
    title_optimization: float
    meta_description: float
    heading_structure: float
    internal_linking: float
    schema_markup: float
    keyword_relevance: float
    keyword_density: float
    semantic_keywords: float
    page_speed: float
    mobile_friendly: float
    accessibility: float


class GEOScoreDetailResponse(BaseModel):
    """GEO评分详情响应"""
    overall_score: float
    grade: str
    visibility_estimate: str
    category_scores: Dict[str, float]
    factors: GEOFactorsResponse
    recommendations: List[str]
    score_history: List[Dict[str, Any]]
    last_updated: datetime


class GEOScoreRequest(BaseModel):
    """GEO评分请求"""
    url: Optional[str] = Field(None, description="要评分的URL")
    content: Optional[str] = Field(None, description="直接提供的内容")
    title: Optional[str] = Field(None, description="页面标题")
    meta_description: Optional[str] = Field(None, description="Meta描述")
    target_keywords: Optional[List[str]] = Field([], description="目标关键词")
    brand_keywords: Optional[List[str]] = Field([], description="品牌关键词")
    previous_scores: Optional[List[Dict[str, Any]]] = Field([], description="历史评分")


class GEOScoreResponse(BaseModel):
    """GEO评分响应"""
    url: str
    geo_score: GEOScoreDetailResponse
    analysis_summary: Dict[str, float]


# 批量分析相关模式
class BatchAnalysisRequest(BaseModel):
    """批量分析请求"""
    urls: List[str] = Field(..., description="要分析的URL列表")
    target_keywords: Optional[List[str]] = Field([], description="目标关键词")
    max_concurrent: Optional[int] = Field(3, description="最大并发数")
    delay_between_requests: Optional[float] = Field(2.0, description="请求间延迟")
    
    @validator("urls")
    def validate_urls(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 URLs allowed")
        for url in v:
            if not url.startswith(("http://", "https://")):
                raise ValueError(f"Invalid URL: {url}")
        return v


class BatchAnalysisResponse(BaseModel):
    """批量分析响应"""
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    analysis_time: float


# 配置模式
class AnalysisConfig(BaseModel):
    """分析配置"""
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
