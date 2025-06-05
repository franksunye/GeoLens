"""
引用检测服务
提供完整的引用检测功能，包括AI模型调用和品牌分析
"""

import asyncio
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 延迟导入避免循环依赖
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.base import BusinessService
from app.services.ai import AIServiceFactory, AIMessage, AIRole
from app.services.brand_detection import ImprovedBrandDetector
from app.models.mention import create_mention_check, create_mention_result, create_brand_mention
from app.api.v1.mention_detection import (
    MentionCheckResponse, ModelResult, BrandMention,
    HistoryResponse, HistoryItem, SavePromptResponse
)


@dataclass
class MentionDetectionConfig:
    """引用检测配置"""
    models: List[str]
    api_keys: Dict[str, str]
    max_tokens: int = 300
    temperature: float = 0.3
    timeout: int = 30
    parallel_execution: bool = True


class MentionDetectionService:
    """引用检测服务"""
    
    def __init__(self, db=None):
        self._db = db
        self._ai_factory = None
        self._repository = None
        self.brand_detector = ImprovedBrandDetector()
        self._model_mapping = {
            "doubao": "doubao-1-5-lite-32k-250115",
            "deepseek": "deepseek-reasoner",
            "openai": "gpt-3.5-turbo",
            "claude": "claude-3-sonnet-20240229"
        }

    @property
    def db(self):
        """获取数据库会话"""
        if self._db is None:
            raise RuntimeError("Database session not initialized")
        return self._db

    @property
    def ai_factory(self):
        """获取AI服务工厂"""
        if self._ai_factory is None:
            self._ai_factory = AIServiceFactory()
        return self._ai_factory

    @property
    def repository(self):
        """获取数据仓库"""
        if self._repository is None:
            from app.repositories.mention_repository import MentionRepository
            self._repository = MentionRepository(self.db)
        return self._repository

    async def __aenter__(self):
        """异步上下文管理器入口"""
        if self._db is None:
            from app.core.database import AsyncSessionLocal
            self._db = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self._db:
            if exc_type:
                await self._db.rollback()
            else:
                await self._db.commit()
            await self._db.close()
    
    async def execute_detection(
        self,
        project_id: str,
        user_id: str,
        prompt: str,
        brands: List[str],
        config: MentionDetectionConfig,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MentionCheckResponse:
        """
        执行完整的引用检测流程
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            prompt: 查询提示
            brands: 目标品牌列表
            config: 检测配置
            metadata: 额外元数据
            
        Returns:
            检测结果响应
        """
        check_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # 1. 创建检测记录
        check_data = {
            "id": check_id,
            "project_id": project_id,
            "user_id": user_id,
            "prompt": prompt,
            "brands_checked": json.dumps(brands),
            "models_used": json.dumps(config.models),
            "status": "running",
            "created_at": start_time,
            "extra_metadata": json.dumps(metadata or {})
        }
        
        await self.repository.create_check(check_data)
        
        try:
            # 2. 执行AI模型调用
            if config.parallel_execution:
                model_results = await self._execute_models_parallel(
                    check_id, prompt, brands, config
                )
            else:
                model_results = await self._execute_models_sequential(
                    check_id, prompt, brands, config
                )
            
            # 3. 计算汇总统计
            summary = self._calculate_summary(model_results, brands, config.models)
            
            # 4. 更新检测记录
            await self.repository.update_check_status(
                check_id=check_id,
                status="completed",
                completed_at=datetime.now(),
                total_mentions=summary["total_mentions"],
                mention_rate=summary["mention_rate"],
                avg_confidence=summary["avg_confidence"]
            )
            
            return MentionCheckResponse(
                check_id=check_id,
                project_id=project_id,
                prompt=prompt,
                status="completed",
                results=model_results,
                summary=summary,
                created_at=start_time,
                completed_at=datetime.now()
            )
            
        except Exception as e:
            # 更新为失败状态
            await self.repository.update_check_status(check_id, "failed")
            raise e
    
    async def _execute_models_parallel(
        self,
        check_id: str,
        prompt: str,
        brands: List[str],
        config: MentionDetectionConfig
    ) -> List[ModelResult]:
        """并行执行多个AI模型"""
        tasks = [
            self._process_single_model(check_id, model, prompt, brands, config)
            for model in config.models
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        model_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                model_results.append(ModelResult(
                    model=config.models[i],
                    response_text=f"Error: {str(result)}",
                    mentions=[],
                    processing_time_ms=0
                ))
            else:
                model_results.append(result)
        
        return model_results
    
    async def _execute_models_sequential(
        self,
        check_id: str,
        prompt: str,
        brands: List[str],
        config: MentionDetectionConfig
    ) -> List[ModelResult]:
        """串行执行多个AI模型"""
        model_results = []
        
        for model in config.models:
            try:
                result = await self._process_single_model(
                    check_id, model, prompt, brands, config
                )
                model_results.append(result)
            except Exception as e:
                model_results.append(ModelResult(
                    model=model,
                    response_text=f"Error: {str(e)}",
                    mentions=[],
                    processing_time_ms=0
                ))
        
        return model_results
    
    async def _process_single_model(
        self,
        check_id: str,
        model_name: str,
        prompt: str,
        brands: List[str],
        config: MentionDetectionConfig
    ) -> ModelResult:
        """处理单个AI模型"""
        start_time = datetime.now()
        result_id = str(uuid.uuid4())
        
        try:
            # 获取AI提供商
            api_key = config.api_keys.get(f"{model_name.upper()}_API_KEY") or config.api_keys.get(model_name)
            if not api_key:
                raise ValueError(f"缺少 {model_name} 的API密钥")
            
            provider = self.ai_factory.get_provider(model_name, api_key=api_key)
            model_id = self._model_mapping.get(model_name, model_name)
            
            # 执行AI调用
            messages = [AIMessage(role=AIRole.USER, content=prompt)]
            response = await provider.chat_completion(
                messages=messages,
                model=model_id,
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # 保存模型结果
            result_data = {
                "id": result_id,
                "check_id": check_id,
                "model": model_name,
                "response_text": response.content,
                "processing_time_ms": processing_time
            }
            await self.repository.save_result(result_data)
            
            # 分析品牌提及
            brand_analysis = self.brand_detector.detect_brand_mentions(response.content, brands)
            mentions = self._convert_to_api_format(brand_analysis)
            
            # 保存品牌提及
            mentions_data = []
            for mention in mentions:
                mention_data = {
                    "id": str(uuid.uuid4()),
                    "result_id": result_id,
                    "brand": mention.brand,
                    "mentioned": mention.mentioned,
                    "confidence_score": mention.confidence_score,
                    "context_snippet": mention.context_snippet,
                    "position": mention.position
                }
                mentions_data.append(mention_data)
            
            await self.repository.save_mentions(mentions_data)
            
            return ModelResult(
                model=model_name,
                response_text=response.content,
                mentions=mentions,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # 保存错误结果
            result_data = {
                "id": result_id,
                "check_id": check_id,
                "model": model_name,
                "response_text": f"Error calling {model_name}: {str(e)}",
                "processing_time_ms": processing_time,
                "error_message": str(e)
            }
            await self.repository.save_result(result_data)
            
            raise e
    
    def _convert_to_api_format(self, brand_analysis: Dict) -> List[BrandMention]:
        """转换品牌分析结果为API格式"""
        mentions = []
        for brand, analysis in brand_analysis.items():
            mentions.append(BrandMention(
                brand=brand,
                mentioned=analysis.mentioned,
                confidence_score=analysis.confidence,
                context_snippet=analysis.contexts[0] if analysis.contexts else None,
                position=analysis.positions[0] if analysis.positions else None
            ))
        return mentions
    
    def _calculate_summary(
        self,
        model_results: List[ModelResult],
        brands: List[str],
        models: List[str]
    ) -> Dict[str, Any]:
        """计算汇总统计"""
        total_mentions = sum(
            len([m for m in result.mentions if m.mentioned])
            for result in model_results
        )
        
        mention_rate = total_mentions / (len(brands) * len(models)) if brands and models else 0
        
        brands_mentioned = list(set([
            mention.brand
            for result in model_results
            for mention in result.mentions
            if mention.mentioned
        ]))
        
        avg_confidence = 0
        if total_mentions > 0:
            all_confidences = [
                mention.confidence_score
                for result in model_results
                for mention in result.mentions
                if mention.mentioned
            ]
            avg_confidence = sum(all_confidences) / len(all_confidences)
        
        return {
            "total_mentions": total_mentions,
            "brands_mentioned": brands_mentioned,
            "mention_rate": round(mention_rate, 4),
            "avg_confidence": round(avg_confidence, 4)
        }
    
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """实现基类的抽象方法"""
        return await self.execute_detection(*args, **kwargs)


# 移除服务注册避免循环导入
