"""
引用检测数据访问层

使用Repository模式封装数据库操作，提供清晰的数据访问接口。
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, update, delete
from sqlalchemy.orm import selectinload

from app.models.mention import (
    MentionCheck, MentionResult, BrandMention, 
    PromptTemplate, AnalyticsCache
)


class MentionRepository:
    """引用检测数据访问层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== MentionCheck 操作 ====================
    
    async def create_check(self, check_data: Dict[str, Any]) -> MentionCheck:
        """创建引用检测记录"""
        check = MentionCheck(**check_data)
        self.db.add(check)
        await self.db.flush()  # 只flush，不commit
        return check
    
    async def get_check_by_id(self, check_id: str) -> Optional[MentionCheck]:
        """根据ID获取检测记录"""
        result = await self.db.execute(
            select(MentionCheck)
            .options(selectinload(MentionCheck.results).selectinload(MentionResult.mentions))
            .where(MentionCheck.id == check_id)
        )
        return result.scalar_one_or_none()
    
    async def get_checks_by_project(
        self, 
        project_id: str, 
        page: int = 1, 
        limit: int = 20,
        brand_filter: Optional[str] = None,
        model_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[MentionCheck]:
        """获取项目的检测记录"""
        query = select(MentionCheck).where(MentionCheck.project_id == project_id)
        
        # 应用过滤器
        if brand_filter:
            query = query.where(MentionCheck.brands_checked.contains(brand_filter))
        
        if model_filter:
            query = query.where(MentionCheck.models_used.contains(model_filter))
            
        if status_filter:
            query = query.where(MentionCheck.status == status_filter)
        
        # 排序和分页
        query = query.order_by(desc(MentionCheck.created_at))
        query = query.offset((page - 1) * limit).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_check_status(
        self, 
        check_id: str, 
        status: str, 
        completed_at: Optional[datetime] = None,
        total_mentions: Optional[int] = None,
        mention_rate: Optional[float] = None,
        avg_confidence: Optional[float] = None
    ) -> bool:
        """更新检测记录状态"""
        update_data = {"status": status}
        
        if completed_at:
            update_data["completed_at"] = completed_at
        if total_mentions is not None:
            update_data["total_mentions"] = total_mentions
        if mention_rate is not None:
            update_data["mention_rate"] = mention_rate
        if avg_confidence is not None:
            update_data["avg_confidence"] = avg_confidence
        
        result = await self.db.execute(
            update(MentionCheck)
            .where(MentionCheck.id == check_id)
            .values(**update_data)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_checks_count_by_project(self, project_id: str) -> int:
        """获取项目的检测记录总数"""
        result = await self.db.execute(
            select(func.count(MentionCheck.id))
            .where(MentionCheck.project_id == project_id)
        )
        return result.scalar()
    
    # ==================== MentionResult 操作 ====================
    
    async def save_result(self, result_data: Dict[str, Any]) -> MentionResult:
        """保存模型检测结果"""
        result = MentionResult(**result_data)
        self.db.add(result)
        await self.db.flush()  # 只flush，不commit
        return result
    
    async def get_results_by_check(self, check_id: str) -> List[MentionResult]:
        """获取检测记录的所有结果"""
        result = await self.db.execute(
            select(MentionResult)
            .options(selectinload(MentionResult.mentions))
            .where(MentionResult.check_id == check_id)
        )
        return result.scalars().all()
    
    # ==================== BrandMention 操作 ====================
    
    async def save_mentions(self, mentions_data: List[Dict[str, Any]]) -> List[BrandMention]:
        """批量保存品牌提及"""
        mentions = [BrandMention(**data) for data in mentions_data]
        self.db.add_all(mentions)
        await self.db.flush()  # 只flush，不commit
        return mentions
    
    async def get_mentions_by_result(self, result_id: str) -> List[BrandMention]:
        """获取结果的所有品牌提及"""
        result = await self.db.execute(
            select(BrandMention).where(BrandMention.result_id == result_id)
        )
        return result.scalars().all()
    
    # ==================== 统计分析 ====================
    
    async def get_brand_mention_stats(
        self, 
        project_id: str, 
        brand: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """获取品牌提及统计"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # 总检测次数
        total_checks_result = await self.db.execute(
            select(func.count(MentionCheck.id))
            .where(
                and_(
                    MentionCheck.project_id == project_id,
                    MentionCheck.brands_checked.contains(brand),
                    MentionCheck.created_at >= since_date
                )
            )
        )
        total_checks = total_checks_result.scalar()
        
        # 总提及次数
        total_mentions_result = await self.db.execute(
            select(func.count(BrandMention.id))
            .join(MentionResult, BrandMention.result_id == MentionResult.id)
            .join(MentionCheck, MentionResult.check_id == MentionCheck.id)
            .where(
                and_(
                    MentionCheck.project_id == project_id,
                    BrandMention.brand == brand,
                    BrandMention.mentioned == True,
                    MentionCheck.created_at >= since_date
                )
            )
        )
        total_mentions = total_mentions_result.scalar()
        
        # 平均置信度
        avg_confidence_result = await self.db.execute(
            select(func.avg(BrandMention.confidence_score))
            .join(MentionResult, BrandMention.result_id == MentionResult.id)
            .join(MentionCheck, MentionResult.check_id == MentionCheck.id)
            .where(
                and_(
                    MentionCheck.project_id == project_id,
                    BrandMention.brand == brand,
                    BrandMention.mentioned == True,
                    MentionCheck.created_at >= since_date
                )
            )
        )
        avg_confidence = avg_confidence_result.scalar() or 0.0
        
        return {
            "brand": brand,
            "timeframe": f"{days}d",
            "total_checks": total_checks,
            "total_mentions": total_mentions,
            "mention_rate": total_mentions / total_checks if total_checks > 0 else 0.0,
            "avg_confidence": float(avg_confidence),
            "model_performance": {}  # 简化版本
        }
    
    async def get_brand_comparison_stats(
        self, 
        project_id: str, 
        brands: List[str], 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """获取多品牌对比统计"""
        comparison_data = []
        
        for brand in brands:
            stats = await self.get_brand_mention_stats(project_id, brand, days)
            comparison_data.append({
                "brand": brand,
                "mention_rate": stats["mention_rate"],
                "avg_confidence": stats["avg_confidence"],
                "total_mentions": stats["total_mentions"],
                "total_checks": stats["total_checks"]
            })
        
        return comparison_data
    
    # ==================== PromptTemplate 操作 ====================
    
    async def save_template(self, template_data: Dict[str, Any]) -> PromptTemplate:
        """保存Prompt模板"""
        template = PromptTemplate(**template_data)
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template
    
    async def get_templates_by_user(
        self, 
        user_id: str, 
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[PromptTemplate]:
        """获取用户的模板列表"""
        query = select(PromptTemplate).where(
            or_(
                PromptTemplate.user_id == user_id,
                PromptTemplate.is_public == True
            )
        )
        
        if category:
            query = query.where(PromptTemplate.category == category)
        
        query = query.order_by(desc(PromptTemplate.usage_count), desc(PromptTemplate.created_at))
        query = query.offset((page - 1) * limit).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def increment_template_usage(self, template_id: str) -> bool:
        """增加模板使用次数"""
        result = await self.db.execute(
            update(PromptTemplate)
            .where(PromptTemplate.id == template_id)
            .values(usage_count=PromptTemplate.usage_count + 1)
        )
        await self.db.commit()
        return result.rowcount > 0
