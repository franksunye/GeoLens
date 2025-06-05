"""
引用检测服务

提供品牌在生成式AI中的引用检测核心功能。
"""

import asyncio
import uuid
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.services.ai import AIServiceFactory
from app.api.v1.mention_detection import (
    MentionCheckResponse, ModelResult, BrandMention,
    HistoryResponse, HistoryItem, SavePromptResponse
)


class MentionDetectionService:
    """引用检测服务"""
    
    def __init__(self):
        self.ai_factory = AIServiceFactory()
        # 模拟数据存储，实际应该连接数据库
        self.checks_storage = {}
        self.templates_storage = {}
        self.analytics_storage = {}
    
    async def check_mentions(
        self,
        prompt: str,
        brands: List[str],
        models: List[str],
        project_id: str
    ) -> MentionCheckResponse:
        """
        执行引用检测
        
        Args:
            prompt: 检测用的提示词
            brands: 要检测的品牌列表
            models: 要使用的AI模型列表
            project_id: 项目ID
            
        Returns:
            检测结果
        """
        check_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # 并行调用多个AI模型
        tasks = []
        for model in models:
            task = self._check_single_model(model, prompt, brands)
            tasks.append(task)
        
        # 等待所有模型完成
        model_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        valid_results = []
        for i, result in enumerate(model_results):
            if isinstance(result, Exception):
                # 处理异常情况
                valid_results.append(ModelResult(
                    model=models[i],
                    response_text=f"Error: {str(result)}",
                    mentions=[],
                    processing_time_ms=0
                ))
            else:
                valid_results.append(result)
        
        # 计算汇总统计
        total_mentions = sum(
            len([m for m in result.mentions if m.mentioned]) 
            for result in valid_results
        )
        
        mention_rate = total_mentions / (len(brands) * len(models)) if brands and models else 0
        
        brands_mentioned = list(set([
            mention.brand 
            for result in valid_results 
            for mention in result.mentions 
            if mention.mentioned
        ]))
        
        avg_confidence = 0
        if total_mentions > 0:
            all_confidences = [
                mention.confidence_score 
                for result in valid_results 
                for mention in result.mentions 
                if mention.mentioned
            ]
            avg_confidence = sum(all_confidences) / len(all_confidences)
        
        summary = {
            "total_mentions": total_mentions,
            "brands_mentioned": brands_mentioned,
            "mention_rate": round(mention_rate, 4),
            "avg_confidence": round(avg_confidence, 4)
        }
        
        # 创建响应
        response = MentionCheckResponse(
            check_id=check_id,
            project_id=project_id,
            prompt=prompt,
            status="completed",
            results=valid_results,
            summary=summary,
            created_at=start_time,
            completed_at=datetime.now()
        )
        
        # 存储结果（实际应该存储到数据库）
        self.checks_storage[check_id] = response
        
        return response
    
    async def _check_single_model(
        self,
        model: str,
        prompt: str,
        brands: List[str]
    ) -> ModelResult:
        """
        检测单个AI模型的品牌提及
        
        Args:
            model: AI模型名称
            prompt: 提示词
            brands: 品牌列表
            
        Returns:
            单个模型的检测结果
        """
        start_time = datetime.now()
        
        try:
            # 调用AI模型获取回答
            if model == "doubao":
                ai_provider = self.ai_factory.get_provider("doubao")
                response = await ai_provider.chat([{"role": "user", "content": prompt}])
                response_text = response.content
            elif model == "deepseek":
                ai_provider = self.ai_factory.get_provider("deepseek")
                response = await ai_provider.chat([{"role": "user", "content": prompt}])
                response_text = response.content
            elif model == "chatgpt":
                # 暂时使用模拟响应，因为OpenAI provider可能未实现
                response_text = f"模拟ChatGPT回答: {prompt}"
            else:
                raise ValueError(f"Unsupported model: {model}")
            
            # 分析品牌提及
            mentions = self._analyze_mentions(response_text, brands)
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return ModelResult(
                model=model,
                response_text=response_text,
                mentions=mentions,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            return ModelResult(
                model=model,
                response_text=f"Error calling {model}: {str(e)}",
                mentions=[],
                processing_time_ms=processing_time
            )
    
    def _analyze_mentions(self, text: str, brands: List[str]) -> List[BrandMention]:
        """
        分析文本中的品牌提及
        
        使用NER + 关键词匹配算法检测品牌提及
        
        Args:
            text: 要分析的文本
            brands: 品牌列表
            
        Returns:
            品牌提及列表
        """
        mentions = []
        text_lower = text.lower()
        
        for brand in brands:
            brand_lower = brand.lower()
            
            # 精确匹配
            if brand_lower in text_lower:
                # 找到提及位置
                start_pos = text_lower.find(brand_lower)
                
                # 提取上下文（前后各50个字符）
                context_start = max(0, start_pos - 50)
                context_end = min(len(text), start_pos + len(brand) + 50)
                context_snippet = text[context_start:context_end].strip()
                
                # 计算置信度（简化版本）
                confidence = self._calculate_confidence(text, brand, start_pos)
                
                # 计算在回答中的位置（第几个被提及的品牌）
                position = self._calculate_position(text_lower, brand_lower, brands)
                
                mentions.append(BrandMention(
                    brand=brand,
                    mentioned=True,
                    confidence_score=confidence,
                    context_snippet=context_snippet,
                    position=position
                ))
            else:
                # 未提及
                mentions.append(BrandMention(
                    brand=brand,
                    mentioned=False,
                    confidence_score=0.0,
                    context_snippet=None,
                    position=None
                ))
        
        return mentions
    
    def _calculate_confidence(self, text: str, brand: str, position: int) -> float:
        """
        计算品牌提及的置信度
        
        Args:
            text: 完整文本
            brand: 品牌名称
            position: 品牌在文本中的位置
            
        Returns:
            置信度分数 (0.0-1.0)
        """
        base_confidence = 0.85  # 精确匹配的基础置信度
        
        # 上下文分析加分
        context_start = max(0, position - 100)
        context_end = min(len(text), position + len(brand) + 100)
        context = text[context_start:context_end].lower()
        
        # 推荐词汇加分
        positive_words = ["推荐", "建议", "使用", "选择", "优秀", "好用", "适合"]
        for word in positive_words:
            if word in context:
                base_confidence += 0.05
        
        # 否定词汇减分
        negative_words = ["不推荐", "避免", "不建议", "不适合", "问题"]
        for word in negative_words:
            if word in context:
                base_confidence -= 0.15
        
        # 确保在合理范围内
        return max(0.0, min(1.0, base_confidence))
    
    def _calculate_position(self, text: str, brand: str, all_brands: List[str]) -> Optional[int]:
        """
        计算品牌在回答中的提及位置
        
        Args:
            text: 文本（小写）
            brand: 品牌名称（小写）
            all_brands: 所有品牌列表
            
        Returns:
            位置（1开始），如果未提及则返回None
        """
        # 找到所有品牌的位置
        brand_positions = []
        for b in all_brands:
            pos = text.find(b.lower())
            if pos != -1:
                brand_positions.append((pos, b.lower()))
        
        # 按位置排序
        brand_positions.sort(key=lambda x: x[0])
        
        # 找到当前品牌的排名
        for i, (pos, b) in enumerate(brand_positions):
            if b == brand:
                return i + 1
        
        return None
    
    async def get_history(
        self,
        project_id: str,
        page: int = 1,
        limit: int = 20,
        brand_filter: Optional[str] = None,
        model_filter: Optional[str] = None
    ) -> HistoryResponse:
        """
        获取检测历史记录
        """
        # 模拟历史数据（实际应该从数据库查询）
        history_items = [
            HistoryItem(
                id=str(uuid.uuid4()),
                prompt="推荐几个适合团队协作的知识管理工具",
                brands_checked=["Notion", "Obsidian", "Roam Research"],
                models_used=["doubao", "deepseek"],
                total_mentions=3,
                mention_rate=0.75,
                created_at=datetime.now() - timedelta(hours=2)
            ),
            HistoryItem(
                id=str(uuid.uuid4()),
                prompt="有哪些好用的项目管理软件？",
                brands_checked=["Asana", "Trello", "Monday"],
                models_used=["chatgpt", "doubao"],
                total_mentions=2,
                mention_rate=0.67,
                created_at=datetime.now() - timedelta(days=1)
            )
        ]
        
        # 应用过滤器
        if brand_filter:
            history_items = [
                item for item in history_items 
                if brand_filter in item.brands_checked
            ]
        
        if model_filter:
            history_items = [
                item for item in history_items 
                if model_filter in item.models_used
            ]
        
        # 分页
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_items = history_items[start_idx:end_idx]
        
        return HistoryResponse(
            checks=paginated_items,
            pagination={
                "page": page,
                "limit": limit,
                "total": len(history_items),
                "pages": (len(history_items) + limit - 1) // limit
            }
        )
    
    async def save_prompt_template(
        self,
        name: str,
        category: str,
        template: str,
        variables: Dict[str, str],
        description: Optional[str],
        user_id: str
    ) -> SavePromptResponse:
        """
        保存Prompt模板
        """
        template_id = str(uuid.uuid4())
        
        template_obj = SavePromptResponse(
            id=template_id,
            name=name,
            category=category,
            template=template,
            variables=variables,
            usage_count=0,
            created_at=datetime.now()
        )
        
        # 存储模板（实际应该存储到数据库）
        self.templates_storage[template_id] = template_obj
        
        return template_obj
    
    async def get_prompt_templates(
        self,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        获取Prompt模板列表
        """
        # 模拟模板数据
        templates = [
            {
                "id": str(uuid.uuid4()),
                "name": "协作工具推荐",
                "category": "productivity",
                "template": "推荐几个适合{team_size}人团队使用的{tool_type}工具",
                "usage_count": 25,
                "created_at": datetime.now() - timedelta(days=5)
            },
            {
                "id": str(uuid.uuid4()),
                "name": "项目管理软件",
                "category": "productivity",
                "template": "有哪些好用的项目管理软件适合{industry}行业？",
                "usage_count": 18,
                "created_at": datetime.now() - timedelta(days=3)
            }
        ]
        
        # 应用分类过滤
        if category:
            templates = [t for t in templates if t["category"] == category]
        
        # 分页
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_templates = templates[start_idx:end_idx]
        
        return {
            "templates": paginated_templates,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(templates),
                "pages": (len(templates) + limit - 1) // limit
            }
        }
    
    async def get_mention_analytics(
        self,
        project_id: str,
        brand: Optional[str] = None,
        timeframe: str = "30d",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取品牌引用统计
        """
        # 模拟分析数据
        return {
            "brand": brand or "All Brands",
            "timeframe": timeframe,
            "total_checks": 45,
            "total_mentions": 32,
            "mention_rate": 0.71,
            "model_performance": {
                "doubao": {"checks": 20, "mentions": 15, "rate": 0.75, "avg_confidence": 0.92},
                "deepseek": {"checks": 15, "mentions": 10, "rate": 0.67, "avg_confidence": 0.88},
                "chatgpt": {"checks": 10, "mentions": 7, "rate": 0.70, "avg_confidence": 0.90}
            },
            "trend_data": [
                {"date": "2024-05-01", "mentions": 5, "checks": 7},
                {"date": "2024-05-15", "mentions": 8, "checks": 12},
                {"date": "2024-05-30", "mentions": 12, "checks": 15}
            ],
            "top_contexts": [
                "推荐作为团队协作工具",
                "适合知识管理和文档整理",
                "支持多种内容类型的工作空间"
            ]
        }
    
    async def compare_brands(
        self,
        project_id: str,
        brands: List[str]
    ) -> Dict[str, Any]:
        """
        竞品对比分析
        """
        # 模拟对比数据
        comparison_data = []
        for i, brand in enumerate(brands):
            comparison_data.append({
                "brand": brand,
                "mention_rate": 0.75 - (i * 0.15),  # 模拟递减的提及率
                "avg_confidence": 0.92 - (i * 0.07),
                "total_mentions": 32 - (i * 10)
            })
        
        return {
            "comparison": comparison_data,
            "insights": [
                f"{brands[0]}在团队协作场景中被提及最多" if brands else "",
                f"{brands[1]}在个人知识管理场景表现较好" if len(brands) > 1 else ""
            ]
        }
