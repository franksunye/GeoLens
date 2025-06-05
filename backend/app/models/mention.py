"""
引用检测相关的数据模型

包含引用检测记录、模型结果、品牌提及等数据模型。
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MentionCheck(Base):
    """引用检测记录表"""
    __tablename__ = "mention_checks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    brands_checked = Column(Text, nullable=False)  # JSON数组: ["Notion", "Obsidian"]
    models_used = Column(Text, nullable=False)     # JSON数组: ["doubao", "deepseek"]
    status = Column(String, nullable=False, default="pending", index=True)  # pending/running/completed/failed
    total_mentions = Column(Integer, default=0)
    mention_rate = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now(), index=True)
    completed_at = Column(DateTime)
    extra_metadata = Column(Text)  # JSON: 额外元数据
    
    # 关系
    results = relationship("MentionResult", back_populates="check", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MentionCheck(id={self.id}, project_id={self.project_id}, status={self.status})>"


class MentionResult(Base):
    """模型检测结果表"""
    __tablename__ = "mention_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    check_id = Column(String, ForeignKey("mention_checks.id"), nullable=False, index=True)
    model = Column(String, nullable=False, index=True)  # doubao/deepseek/chatgpt
    response_text = Column(Text, nullable=False)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # 关系
    check = relationship("MentionCheck", back_populates="results")
    mentions = relationship("BrandMention", back_populates="result", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MentionResult(id={self.id}, model={self.model}, check_id={self.check_id})>"


class BrandMention(Base):
    """品牌提及详情表"""
    __tablename__ = "brand_mentions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    result_id = Column(String, ForeignKey("mention_results.id"), nullable=False, index=True)
    brand = Column(String, nullable=False, index=True)
    mentioned = Column(Boolean, nullable=False, index=True)
    confidence_score = Column(Float, nullable=False)
    context_snippet = Column(Text)
    position = Column(Integer)  # 提及位置(第几个)
    created_at = Column(DateTime, default=func.now())
    
    # 关系
    result = relationship("MentionResult", back_populates="mentions")
    
    def __repr__(self):
        return f"<BrandMention(id={self.id}, brand={self.brand}, mentioned={self.mentioned})>"


class PromptTemplate(Base):
    """Prompt模板表"""
    __tablename__ = "prompt_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)  # productivity/comparison/recommendation
    template = Column(Text, nullable=False)
    variables = Column(Text)  # JSON: 变量定义
    description = Column(Text)
    usage_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<PromptTemplate(id={self.id}, name={self.name}, category={self.category})>"


class AnalyticsCache(Base):
    """统计分析缓存表"""
    __tablename__ = "analytics_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String, unique=True, nullable=False, index=True)
    project_id = Column(String, index=True)
    brand = Column(String, index=True)
    timeframe = Column(String)  # 7d/30d/90d
    data = Column(Text, nullable=False)  # JSON: 统计数据
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<AnalyticsCache(id={self.id}, cache_key={self.cache_key})>"


# 辅助函数
def create_mention_check(
    project_id: str,
    user_id: str,
    prompt: str,
    brands: List[str],
    models: List[str],
    metadata: Optional[dict] = None
) -> MentionCheck:
    """创建引用检测记录的辅助函数"""
    import json
    
    return MentionCheck(
        project_id=project_id,
        user_id=user_id,
        prompt=prompt,
        brands_checked=json.dumps(brands),
        models_used=json.dumps(models),
        extra_metadata=json.dumps(metadata) if metadata else None
    )


def create_mention_result(
    check_id: str,
    model: str,
    response_text: str,
    processing_time_ms: Optional[int] = None,
    error_message: Optional[str] = None
) -> MentionResult:
    """创建模型检测结果的辅助函数"""
    return MentionResult(
        check_id=check_id,
        model=model,
        response_text=response_text,
        processing_time_ms=processing_time_ms,
        error_message=error_message
    )


def create_brand_mention(
    result_id: str,
    brand: str,
    mentioned: bool,
    confidence_score: float,
    context_snippet: Optional[str] = None,
    position: Optional[int] = None
) -> BrandMention:
    """创建品牌提及记录的辅助函数"""
    return BrandMention(
        result_id=result_id,
        brand=brand,
        mentioned=mentioned,
        confidence_score=confidence_score,
        context_snippet=context_snippet,
        position=position
    )


def create_prompt_template(
    user_id: str,
    name: str,
    category: str,
    template: str,
    variables: Optional[dict] = None,
    description: Optional[str] = None,
    is_public: bool = False
) -> PromptTemplate:
    """创建Prompt模板的辅助函数"""
    import json
    
    return PromptTemplate(
        user_id=user_id,
        name=name,
        category=category,
        template=template,
        variables=json.dumps(variables) if variables else None,
        description=description,
        is_public=is_public
    )
