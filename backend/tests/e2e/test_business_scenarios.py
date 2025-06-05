"""
业务场景端到端测试
"""

import pytest
import json
from typing import List, Dict, Any

from app.services.mention_detection import MentionDetectionService
from app.repositories.mention_repository import MentionRepository


@pytest.mark.e2e
class TestBusinessScenarios:
    """业务场景测试"""

    async def test_brand_monitoring_scenario(
        self,
        skip_if_no_api_keys,
        mention_service,
        test_project_data,
        e2e_db_session,
        e2e_config
    ):
        """品牌监控场景测试"""
        print(f"🏢 开始品牌监控场景测试")
        
        # 模拟品牌监控场景：监控Notion在不同查询中的表现
        brand_to_monitor = "Notion"
        monitoring_queries = [
            "推荐几个团队协作工具",
            "有哪些好用的笔记软件？",
            "知识管理系统有什么推荐？",
            "项目管理工具推荐",
            "文档协作平台有哪些？"
        ]
        
        monitoring_results = []
        
        # 对每个查询进行监控
        for i, query in enumerate(monitoring_queries):
            print(f"   监控查询 {i+1}/{len(monitoring_queries)}: {query}")

            # 创建检测配置
            from app.services.mention_detection import MentionDetectionConfig
            config = MentionDetectionConfig(
                models=["doubao", "deepseek"],
                api_keys={
                    "DOUBAO_API_KEY": e2e_config["doubao_api_key"],
                    "DEEPSEEK_API_KEY": e2e_config["deepseek_api_key"]
                },
                max_tokens=300,
                temperature=0.3,
                parallel_execution=False
            )

            result = await mention_service.execute_detection(
                project_id=test_project_data["project_id"],
                user_id=test_project_data["user_id"],
                prompt=query,
                brands=[brand_to_monitor],
                config=config
            )
            
            assert result.status == "completed"
            
            # 收集监控数据
            brand_mentions = []
            for model_result in result.results:
                for mention in model_result.mentions:
                    if mention.brand == brand_to_monitor:
                        brand_mentions.append({
                            "model": model_result.model,
                            "mentioned": mention.mentioned,
                            "confidence": mention.confidence_score,
                            "context": mention.context if hasattr(mention, 'context') else ""
                        })
            
            monitoring_results.append({
                "query": query,
                "check_id": result.check_id,
                "mentions": brand_mentions,
                "total_models": len(result.results)
            })
        
        # 分析监控结果
        total_queries = len(monitoring_results)
        mentioned_count = sum(
            1 for result in monitoring_results 
            if any(mention["mentioned"] for mention in result["mentions"])
        )
        
        mention_rate = mentioned_count / total_queries if total_queries > 0 else 0
        
        # 计算平均置信度
        all_confidences = []
        for result in monitoring_results:
            for mention in result["mentions"]:
                if mention["mentioned"]:
                    all_confidences.append(mention["confidence"])
        
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
        
        # 验证监控结果
        assert total_queries == len(monitoring_queries)
        assert 0 <= mention_rate <= 1
        assert 0 <= avg_confidence <= 1
        
        print(f"✅ 品牌监控场景测试完成")
        print(f"   监控品牌: {brand_to_monitor}")
        print(f"   查询总数: {total_queries}")
        print(f"   被提及次数: {mentioned_count}")
        print(f"   提及率: {mention_rate:.2%}")
        print(f"   平均置信度: {avg_confidence:.2f}")

    async def test_competitor_analysis_scenario(
        self,
        skip_if_no_api_keys,
        mention_service,
        test_project_data,
        e2e_db_session,
        e2e_config
    ):
        """竞品分析场景测试"""
        print(f"🔍 开始竞品分析场景测试")
        
        # 竞品分析：比较多个知识管理工具
        competitors = ["Notion", "Obsidian", "Roam Research", "Logseq"]
        analysis_queries = [
            "比较几个知识管理工具的优缺点",
            "哪个笔记软件最适合研究人员？",
            "团队知识库用什么工具比较好？"
        ]
        
        competitor_analysis = {brand: {"mentions": 0, "total_checks": 0, "confidences": []} 
                             for brand in competitors}
        
        # 对每个查询进行竞品分析
        for i, query in enumerate(analysis_queries):
            print(f"   分析查询 {i+1}/{len(analysis_queries)}: {query}")

            # 创建检测配置
            from app.services.mention_detection import MentionDetectionConfig
            config = MentionDetectionConfig(
                models=["doubao"],  # 使用单个模型减少API调用
                api_keys={"DOUBAO_API_KEY": e2e_config["doubao_api_key"]},
                max_tokens=300,
                temperature=0.3,
                parallel_execution=False
            )

            result = await mention_service.execute_detection(
                project_id=test_project_data["project_id"],
                user_id=test_project_data["user_id"],
                prompt=query,
                brands=competitors,
                config=config
            )
            
            assert result.status == "completed"
            assert len(result.results) == 1  # 一个模型
            
            model_result = result.results[0]
            
            # 分析每个竞品的表现
            for mention in model_result.mentions:
                brand = mention.brand
                competitor_analysis[brand]["total_checks"] += 1
                
                if mention.mentioned:
                    competitor_analysis[brand]["mentions"] += 1
                    competitor_analysis[brand]["confidences"].append(mention.confidence_score)
        
        # 计算竞品分析指标
        analysis_summary = {}
        for brand, data in competitor_analysis.items():
            mention_rate = data["mentions"] / data["total_checks"] if data["total_checks"] > 0 else 0
            avg_confidence = (sum(data["confidences"]) / len(data["confidences"]) 
                            if data["confidences"] else 0)
            
            analysis_summary[brand] = {
                "mention_rate": mention_rate,
                "avg_confidence": avg_confidence,
                "total_mentions": data["mentions"],
                "total_checks": data["total_checks"]
            }
        
        # 验证分析结果
        for brand, summary in analysis_summary.items():
            assert 0 <= summary["mention_rate"] <= 1
            assert 0 <= summary["avg_confidence"] <= 1
            assert summary["total_checks"] == len(analysis_queries)
        
        # 找出表现最好的竞品
        best_performer = max(analysis_summary.items(), 
                           key=lambda x: (x[1]["mention_rate"], x[1]["avg_confidence"]))
        
        print(f"✅ 竞品分析场景测试完成")
        print(f"   分析竞品: {competitors}")
        print(f"   查询数量: {len(analysis_queries)}")
        print(f"   表现最佳: {best_performer[0]} (提及率: {best_performer[1]['mention_rate']:.2%})")
        
        # 打印详细分析结果
        for brand, summary in analysis_summary.items():
            print(f"   {brand}: 提及率 {summary['mention_rate']:.2%}, "
                  f"置信度 {summary['avg_confidence']:.2f}")

    async def test_prompt_optimization_scenario(
        self,
        skip_if_no_api_keys,
        mention_service,
        test_project_data,
        e2e_db_session,
        e2e_config
    ):
        """Prompt优化场景测试"""
        print(f"🎯 开始Prompt优化场景测试")
        
        # 测试不同Prompt对检测结果的影响
        brand = "Notion"
        prompt_variations = [
            "推荐笔记软件",  # 简短直接
            "请推荐几个适合个人使用的笔记软件",  # 中等长度，明确用途
            "我需要一个功能强大的笔记和知识管理工具，能够支持团队协作，请推荐几个选择",  # 详细描述
            "有哪些类似于Notion的工具？",  # 直接提及竞品
            "不要推荐Notion，有其他好用的笔记软件吗？"  # 排除性提问
        ]
        
        optimization_results = []
        
        # 测试每个Prompt变体
        for i, prompt in enumerate(prompt_variations):
            print(f"   测试Prompt {i+1}/{len(prompt_variations)}")

            # 创建检测配置
            from app.services.mention_detection import MentionDetectionConfig
            config = MentionDetectionConfig(
                models=["doubao"],
                api_keys={"DOUBAO_API_KEY": e2e_config["doubao_api_key"]},
                max_tokens=300,
                temperature=0.3,
                parallel_execution=False
            )

            result = await mention_service.execute_detection(
                project_id=test_project_data["project_id"],
                user_id=test_project_data["user_id"],
                prompt=prompt,
                brands=[brand],
                config=config
            )
            
            assert result.status == "completed"
            assert len(result.results) == 1
            
            model_result = result.results[0]
            brand_mention = model_result.mentions[0]  # 只有一个品牌
            
            optimization_results.append({
                "prompt": prompt,
                "prompt_length": len(prompt),
                "mentioned": brand_mention.mentioned,
                "confidence": brand_mention.confidence_score,
                "response_length": len(model_result.response_text),
                "check_id": result.check_id
            })
        
        # 分析Prompt优化效果
        mentioned_prompts = [r for r in optimization_results if r["mentioned"]]
        not_mentioned_prompts = [r for r in optimization_results if not r["mentioned"]]
        
        # 计算统计指标
        total_prompts = len(optimization_results)
        mention_rate = len(mentioned_prompts) / total_prompts
        
        if mentioned_prompts:
            avg_confidence_when_mentioned = sum(r["confidence"] for r in mentioned_prompts) / len(mentioned_prompts)
            avg_prompt_length_when_mentioned = sum(r["prompt_length"] for r in mentioned_prompts) / len(mentioned_prompts)
        else:
            avg_confidence_when_mentioned = 0
            avg_prompt_length_when_mentioned = 0
        
        # 验证优化结果
        assert total_prompts == len(prompt_variations)
        assert 0 <= mention_rate <= 1
        
        print(f"✅ Prompt优化场景测试完成")
        print(f"   测试Prompt数: {total_prompts}")
        print(f"   提及率: {mention_rate:.2%}")
        print(f"   被提及时平均置信度: {avg_confidence_when_mentioned:.2f}")
        print(f"   被提及时平均Prompt长度: {avg_prompt_length_when_mentioned:.0f}字符")
        
        # 打印每个Prompt的结果
        for i, result in enumerate(optimization_results):
            status = "✅" if result["mentioned"] else "❌"
            print(f"   Prompt {i+1} {status}: 置信度 {result['confidence']:.2f} - {result['prompt'][:50]}...")

    async def test_multi_model_consistency_scenario(
        self,
        skip_if_no_api_keys,
        mention_service,
        test_project_data,
        e2e_config
    ):
        """多模型一致性场景测试"""
        print(f"🤖 开始多模型一致性场景测试")
        
        # 测试同一个查询在不同模型中的一致性
        test_queries = [
            "推荐团队协作工具",
            "有哪些好用的笔记软件？"
        ]
        
        brands = ["Notion", "Obsidian"]
        models = ["doubao", "deepseek"]
        
        consistency_results = []
        
        for query in test_queries:
            print(f"   测试查询: {query}")

            # 创建检测配置
            from app.services.mention_detection import MentionDetectionConfig
            config = MentionDetectionConfig(
                models=models,
                api_keys={
                    "DOUBAO_API_KEY": e2e_config["doubao_api_key"],
                    "DEEPSEEK_API_KEY": e2e_config["deepseek_api_key"]
                },
                max_tokens=300,
                temperature=0.3,
                parallel_execution=False
            )

            result = await mention_service.execute_detection(
                project_id=test_project_data["project_id"],
                user_id=test_project_data["user_id"],
                prompt=query,
                brands=brands,
                config=config
            )
            
            assert result.status == "completed"
            assert len(result.results) == len(models)
            
            # 分析模型间的一致性
            brand_consistency = {}
            
            for brand in brands:
                brand_results = []
                for model_result in result.results:
                    brand_mention = next(
                        (m for m in model_result.mentions if m.brand == brand), 
                        None
                    )
                    if brand_mention:
                        brand_results.append({
                            "model": model_result.model,
                            "mentioned": brand_mention.mentioned,
                            "confidence": brand_mention.confidence_score
                        })
                
                # 计算一致性指标
                mentioned_count = sum(1 for r in brand_results if r["mentioned"])
                consistency_rate = mentioned_count / len(brand_results) if brand_results else 0
                
                # 一致性：要么都提及，要么都不提及
                is_consistent = mentioned_count == 0 or mentioned_count == len(brand_results)
                
                brand_consistency[brand] = {
                    "consistency_rate": consistency_rate,
                    "is_consistent": is_consistent,
                    "model_results": brand_results
                }
            
            consistency_results.append({
                "query": query,
                "brand_consistency": brand_consistency,
                "check_id": result.check_id
            })
        
        # 验证一致性结果
        for result in consistency_results:
            for brand, consistency in result["brand_consistency"].items():
                assert 0 <= consistency["consistency_rate"] <= 1
                assert isinstance(consistency["is_consistent"], bool)
                assert len(consistency["model_results"]) == len(models)
        
        # 计算总体一致性
        total_brand_tests = len(consistency_results) * len(brands)
        consistent_tests = sum(
            1 for result in consistency_results
            for brand_consistency in result["brand_consistency"].values()
            if brand_consistency["is_consistent"]
        )
        
        overall_consistency = consistent_tests / total_brand_tests if total_brand_tests > 0 else 0
        
        print(f"✅ 多模型一致性场景测试完成")
        print(f"   测试查询数: {len(test_queries)}")
        print(f"   测试品牌数: {len(brands)}")
        print(f"   模型数: {len(models)}")
        print(f"   总体一致性: {overall_consistency:.2%}")
        
        # 打印详细一致性结果
        for result in consistency_results:
            print(f"   查询: {result['query']}")
            for brand, consistency in result["brand_consistency"].items():
                status = "✅" if consistency["is_consistent"] else "⚠️"
                print(f"     {brand} {status}: 一致性率 {consistency['consistency_rate']:.2%}")
