"""
AI服务相关的Pydantic模式定义
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AIProviderEnum(str, Enum):
    """AI服务提供商枚举"""
    DOUBAO = "doubao"
    DEEPSEEK = "deepseek"


class AIRoleEnum(str, Enum):
    """AI对话角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """聊天消息模式"""
    role: AIRoleEnum = Field(..., description="消息角色")
    content: str = Field(..., min_length=1, description="消息内容")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "请分析这个网页的品牌提及情况"
            }
        }


class ChatRequest(BaseModel):
    """聊天请求模式"""
    messages: List[ChatMessage] = Field(..., min_items=1, description="对话消息列表")
    model: Optional[str] = Field(default=None, description="指定使用的模型")
    provider: Optional[AIProviderEnum] = Field(default=None, description="指定AI服务提供商")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=1000, ge=1, le=8192, description="最大token数")
    stream: bool = Field(default=False, description="是否流式输出")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的品牌监测分析师"
                    },
                    {
                        "role": "user", 
                        "content": "请分析这个网页内容中的品牌提及情况"
                    }
                ],
                "model": "doubao-pro-32k",
                "provider": "doubao",
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
        }


class TokenUsage(BaseModel):
    """Token使用情况"""
    prompt_tokens: int = Field(..., description="输入token数")
    completion_tokens: int = Field(..., description="输出token数")
    total_tokens: int = Field(..., description="总token数")


class ChatResponse(BaseModel):
    """聊天响应模式"""
    content: str = Field(..., description="AI响应内容")
    model: str = Field(..., description="使用的模型")
    provider: str = Field(..., description="AI服务提供商")
    usage: TokenUsage = Field(..., description="Token使用情况")
    response_time: float = Field(..., description="响应时间(秒)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "根据分析，该网页提及了以下品牌...",
                "model": "doubao-pro-32k",
                "provider": "doubao",
                "usage": {
                    "prompt_tokens": 150,
                    "completion_tokens": 200,
                    "total_tokens": 350
                },
                "response_time": 2.5,
                "metadata": {
                    "finish_reason": "stop",
                    "response_id": "chatcmpl-123"
                }
            }
        }


class AIProviderInfo(BaseModel):
    """AI服务提供商信息"""
    name: str = Field(..., description="提供商名称")
    display_name: str = Field(..., description="显示名称")
    supported_models: List[str] = Field(..., description="支持的模型列表")
    available: bool = Field(..., description="是否可用")
    description: str = Field(..., description="提供商描述")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "doubao",
                "display_name": "豆包(火山引擎)",
                "supported_models": ["doubao-pro-32k", "doubao-lite-32k"],
                "available": True,
                "description": "字节跳动旗下的大语言模型服务"
            }
        }


class AIProvidersResponse(BaseModel):
    """AI服务提供商列表响应"""
    providers: List[AIProviderInfo] = Field(..., description="提供商列表")
    default_provider: str = Field(..., description="默认提供商")
    
    class Config:
        json_schema_extra = {
            "example": {
                "providers": [
                    {
                        "name": "doubao",
                        "display_name": "豆包(火山引擎)",
                        "supported_models": ["doubao-pro-32k", "doubao-lite-32k"],
                        "available": True,
                        "description": "字节跳动旗下的大语言模型服务"
                    }
                ],
                "default_provider": "doubao"
            }
        }


class BrandAnalysisRequest(BaseModel):
    """品牌分析请求模式"""
    content: str = Field(..., min_length=1, description="要分析的内容")
    brand_keywords: List[str] = Field(..., min_items=1, description="品牌关键词列表")
    provider: Optional[AIProviderEnum] = Field(default=None, description="指定AI服务提供商")
    detailed: bool = Field(default=False, description="是否需要详细分析")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "这是一篇关于智能手机的文章...",
                "brand_keywords": ["苹果", "iPhone", "Apple"],
                "provider": "doubao",
                "detailed": True
            }
        }


class BrandMention(BaseModel):
    """品牌提及信息"""
    keyword: str = Field(..., description="提及的关键词")
    count: int = Field(..., description="提及次数")
    context: List[str] = Field(..., description="提及上下文")
    sentiment: str = Field(..., description="情感倾向")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")


class BrandAnalysisResponse(BaseModel):
    """品牌分析响应模式"""
    mentions: List[BrandMention] = Field(..., description="品牌提及列表")
    total_mentions: int = Field(..., description="总提及次数")
    overall_sentiment: str = Field(..., description="整体情感倾向")
    analysis_summary: str = Field(..., description="分析摘要")
    provider: str = Field(..., description="使用的AI服务提供商")
    processing_time: float = Field(..., description="处理时间(秒)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mentions": [
                    {
                        "keyword": "苹果",
                        "count": 3,
                        "context": ["苹果公司发布了新产品", "苹果的市场份额"],
                        "sentiment": "positive",
                        "confidence": 0.85
                    }
                ],
                "total_mentions": 3,
                "overall_sentiment": "positive",
                "analysis_summary": "内容中对苹果品牌的提及主要是正面的...",
                "provider": "doubao",
                "processing_time": 1.2
            }
        }
