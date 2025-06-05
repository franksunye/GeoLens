"""
统一的引用检测业务流程服务
整合AI调用、品牌检测、数据持久化的完整流程
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.mention import (
    MentionCheck, MentionResult, BrandMention,
    create_mention_check, create_mention_result, create_brand_mention
)
from app.services.ai import AIServiceFactory, AIMessage, AIRole
from app.services.brand_detection import analyze_brand_mentions


class MentionDetectionService:
    """引用检测服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_factory = AIServiceFactory()
    
    async def execute_mention_detection(
        self,
        project_id: str,
        user_id: str,
        prompt: str,
        brands: List[str],
        models: List[str],
        api_keys: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> MentionCheck:
        """
        执行完整的引用检测流程
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            prompt: 查询提示
            brands: 目标品牌列表
            models: AI模型列表
            api_keys: API密钥字典
            metadata: 额外元数据
            
        Returns:
            检测任务记录
        """
        # 1. 创建检测任务
        mention_check = create_mention_check(
            project_id=project_id,
            user_id=user_id,
            prompt=prompt,
            brands=brands,
            models=models,
            metadata=metadata or {}
        )
        
        self.db.add(mention_check)
        self.db.commit()
        self.db.refresh(mention_check)
        
        print(f"✅ 创建检测任务: {mention_check.id}")
        
        try:
            # 2. 执行AI调用
            total_mentions = 0
            total_confidence = 0.0
            successful_models = 0
            
            for model_name in models:
                try:
                    result = await self._process_single_model(
                        mention_check.id,
                        model_name,
                        prompt,
                        brands,
                        api_keys
                    )
                    
                    if result:
                        successful_models += 1
                        # 统计该模型的提及情况
                        model_mentions = self.db.query(BrandMention).join(MentionResult).filter(
                            MentionResult.id == result.id,
                            BrandMention.mentioned == True
                        ).count()
                        
                        total_mentions += model_mentions
                        
                        # 计算平均置信度
                        avg_confidence = self.db.query(BrandMention).join(MentionResult).filter(
                            MentionResult.id == result.id
                        ).with_entities(BrandMention.confidence_score).all()
                        
                        if avg_confidence:
                            model_avg = sum(c[0] for c in avg_confidence) / len(avg_confidence)
                            total_confidence += model_avg
                
                except Exception as e:
                    print(f"❌ 模型 {model_name} 处理失败: {str(e)}")
                    # 保存错误结果
                    error_result = create_mention_result(
                        check_id=mention_check.id,
                        model=model_name,
                        response_text="",
                        error_message=str(e)
                    )
                    self.db.add(error_result)
                    self.db.commit()
            
            # 3. 更新检测任务统计
            mention_check.total_mentions = total_mentions
            mention_check.mention_rate = total_mentions / (len(brands) * successful_models) if successful_models > 0 else 0.0
            mention_check.avg_confidence = total_confidence / successful_models if successful_models > 0 else 0.0
            mention_check.status = "completed"
            mention_check.completed_at = datetime.now()
            
            self.db.commit()
            
            print(f"✅ 检测任务完成: 总提及数={total_mentions}, 成功模型数={successful_models}")
            
        except Exception as e:
            # 标记任务失败
            mention_check.status = "failed"
            mention_check.completed_at = datetime.now()
            self.db.commit()
            
            print(f"❌ 检测任务失败: {str(e)}")
            raise
        
        return mention_check
    
    async def _process_single_model(
        self,
        check_id: str,
        model_name: str,
        prompt: str,
        brands: List[str],
        api_keys: Dict[str, str]
    ) -> Optional[MentionResult]:
        """处理单个AI模型"""
        
        print(f"🤖 处理模型: {model_name}")
        
        # 获取API密钥
        api_key = api_keys.get(f"{model_name.upper()}_API_KEY") or api_keys.get(model_name)
        if not api_key:
            raise ValueError(f"缺少 {model_name} 的API密钥")
        
        # 获取AI提供商
        provider = self.ai_factory.get_provider(model_name, api_key=api_key)
        
        # 确定模型ID
        model_id = self._get_model_id(model_name)
        
        # 执行AI调用
        start_time = datetime.now()
        messages = [AIMessage(role=AIRole.USER, content=prompt)]
        
        response = await provider.chat_completion(
            messages=messages,
            model=model_id,
            max_tokens=300,
            temperature=0.3
        )
        
        end_time = datetime.now()
        processing_time = int((end_time - start_time).total_seconds() * 1000)
        
        # 保存模型结果
        mention_result = create_mention_result(
            check_id=check_id,
            model=model_name,
            response_text=response.content,
            processing_time_ms=processing_time
        )
        
        self.db.add(mention_result)
        self.db.commit()
        self.db.refresh(mention_result)
        
        print(f"   ✅ 保存模型结果: {len(response.content)} 字符")
        
        # 分析品牌提及
        brand_analysis = analyze_brand_mentions(response.content, brands)
        
        # 保存品牌提及结果
        for brand, analysis in brand_analysis.items():
            brand_mention = create_brand_mention(
                result_id=mention_result.id,
                brand=brand,
                mentioned=analysis['mentioned'],
                confidence_score=analysis['confidence'],
                context_snippet=analysis['contexts'][0] if analysis['contexts'] else ""
            )
            
            self.db.add(brand_mention)
            
            status = "✅" if analysis['mentioned'] else "❌"
            print(f"      {status} {brand} (置信度: {analysis['confidence']:.2f})")
            
            if analysis['contexts']:
                print(f"         上下文: {analysis['contexts'][0][:80]}...")
        
        self.db.commit()
        
        return mention_result
    
    def _get_model_id(self, model_name: str) -> str:
        """获取模型ID"""
        model_mapping = {
            "doubao": "doubao-1-5-lite-32k-250115",
            "deepseek": "deepseek-reasoner",
            "openai": "gpt-3.5-turbo",
            "claude": "claude-3-sonnet-20240229"
        }

        return model_mapping.get(model_name, model_name)
    
    def generate_business_report(self, project_id: str) -> Dict[str, Any]:
        """生成业务报告"""
        
        # 查询项目的所有检测记录
        checks = self.db.query(MentionCheck).filter(
            MentionCheck.project_id == project_id
        ).all()
        
        if not checks:
            return {"error": "没有找到检测记录"}
        
        # 统计总体数据
        total_checks = len(checks)
        completed_checks = len([c for c in checks if c.status == "completed"])
        
        # 品牌分析
        brand_stats = {}
        model_stats = {}
        
        for check in checks:
            results = self.db.query(MentionResult).filter(
                MentionResult.check_id == check.id
            ).all()
            
            for result in results:
                # 模型统计
                if result.model not in model_stats:
                    model_stats[result.model] = {
                        "total_calls": 0,
                        "successful_calls": 0,
                        "total_mentions": 0,
                        "total_brands": 0,
                        "avg_response_length": 0,
                        "avg_processing_time": 0
                    }
                
                stats = model_stats[result.model]
                stats["total_calls"] += 1
                
                if not result.error_message:
                    stats["successful_calls"] += 1
                    stats["avg_response_length"] += len(result.response_text or "")
                    if result.processing_time_ms:
                        stats["avg_processing_time"] += result.processing_time_ms
                
                # 品牌统计
                mentions = self.db.query(BrandMention).filter(
                    BrandMention.result_id == result.id
                ).all()
                
                for mention in mentions:
                    if mention.brand not in brand_stats:
                        brand_stats[mention.brand] = {
                            "total_checks": 0,
                            "total_mentions": 0,
                            "avg_confidence": 0.0,
                            "contexts": []
                        }
                    
                    brand_stat = brand_stats[mention.brand]
                    brand_stat["total_checks"] += 1
                    stats["total_brands"] += 1
                    
                    if mention.mentioned:
                        brand_stat["total_mentions"] += 1
                        brand_stat["avg_confidence"] += mention.confidence_score
                        stats["total_mentions"] += 1
                        
                        if mention.context_snippet:
                            brand_stat["contexts"].append(mention.context_snippet)
        
        # 计算平均值
        for model, stats in model_stats.items():
            if stats["successful_calls"] > 0:
                stats["avg_response_length"] /= stats["successful_calls"]
                stats["avg_processing_time"] /= stats["successful_calls"]
                stats["success_rate"] = stats["successful_calls"] / stats["total_calls"]
                stats["mention_rate"] = stats["total_mentions"] / max(stats["total_brands"], 1)
        
        for brand, stats in brand_stats.items():
            if stats["total_mentions"] > 0:
                stats["avg_confidence"] /= stats["total_mentions"]
            stats["mention_rate"] = stats["total_mentions"] / max(stats["total_checks"], 1)
        
        return {
            "project_id": project_id,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_checks": total_checks,
                "completed_checks": completed_checks,
                "completion_rate": completed_checks / total_checks if total_checks > 0 else 0
            },
            "brand_analysis": brand_stats,
            "model_analysis": model_stats
        }


# 便捷函数
async def quick_mention_detection(
    prompt: str,
    brands: List[str],
    models: List[str] = ["doubao"],
    api_keys: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    快速引用检测（用于测试）
    """
    import os
    
    # 默认API密钥
    if api_keys is None:
        api_keys = {
            "DOUBAO_API_KEY": os.getenv("DOUBAO_API_KEY"),
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY")
        }
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        service = MentionDetectionService(db)
        
        # 生成测试ID
        project_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # 执行检测
        result = await service.execute_mention_detection(
            project_id=project_id,
            user_id=user_id,
            prompt=prompt,
            brands=brands,
            models=models,
            api_keys=api_keys,
            metadata={"test": True}
        )
        
        # 生成报告
        report = service.generate_business_report(project_id)
        
        return {
            "check_id": result.id,
            "status": result.status,
            "report": report
        }
    
    finally:
        db.close()
