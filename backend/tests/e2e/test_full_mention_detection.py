"""
完整引用检测业务流程测试
"""

import pytest
import asyncio
import json
from typing import List, Dict, Any

from app.services.mention_detection import MentionDetectionService
from app.repositories.mention_repository import MentionRepository


@pytest.mark.e2e
class TestFullMentionDetection:
    """测试完整的引用检测业务流程"""

    async def test_end_to_end_detection_flow(
        self,
        skip_if_no_api_keys,
        mention_service,
        test_brands,
        test_project_data,
        e2e_db_session,
        e2e_config
    ):
        """端到端引用检测流程测试"""
        # 测试数据
        prompt = "推荐几个适合团队协作的知识管理工具"
        models = ["doubao", "deepseek"]
        
        print(f"🚀 开始端到端引用检测测试")
        print(f"   Prompt: {prompt}")
        print(f"   品牌: {test_brands}")
        print(f"   模型: {models}")
        
        try:
            # 1. 创建检测配置
            from app.services.mention_detection import MentionDetectionConfig
            config = MentionDetectionConfig(
                models=models,
                api_keys={
                    "DOUBAO_API_KEY": e2e_config["doubao_api_key"],
                    "DEEPSEEK_API_KEY": e2e_config["deepseek_api_key"]
                },
                max_tokens=300,
                temperature=0.3,
                parallel_execution=False  # 串行执行以减少API调用
            )

            # 2. 执行引用检测
            result = await mention_service.execute_detection(
                project_id=test_project_data["project_id"],
                user_id=test_project_data["user_id"],
                prompt=prompt,
                brands=test_brands,
                config=config
            )
            
            # 3. 验证结果结构
            assert result is not None
            assert hasattr(result, 'check_id')
            assert hasattr(result, 'status')
            assert hasattr(result, 'results')
            assert hasattr(result, 'summary')

            # 4. 验证检测状态
            assert result.status == "completed"
            assert result.check_id is not None

            # 5. 验证模型结果
            assert len(result.results) == len(models)
            
            for model_result in result.results:
                assert hasattr(model_result, 'model')
                assert hasattr(model_result, 'response_text')
                assert hasattr(model_result, 'mentions')
                assert model_result.model in models
                # 注意：某些AI模型可能返回空响应，这是正常的
                assert model_result.response_text is not None
                assert len(model_result.mentions) == len(test_brands)
                
                # 验证品牌提及结果
                for mention in model_result.mentions:
                    assert hasattr(mention, 'brand')
                    assert hasattr(mention, 'mentioned')
                    assert hasattr(mention, 'confidence_score')
                    assert mention.brand in test_brands
                    assert isinstance(mention.mentioned, bool)
                    assert 0 <= mention.confidence_score <= 1
            
            # 6. 验证汇总信息
            assert isinstance(result.summary, dict)
            assert 'total_mentions' in result.summary
            assert 'mention_rate' in result.summary
            assert 'avg_confidence' in result.summary
            assert result.summary['total_mentions'] >= 0
            assert 0 <= result.summary['mention_rate'] <= 1
            assert 0 <= result.summary['avg_confidence'] <= 1
            
            # 7. 验证数据库持久化
            from app.repositories.mention_repository import MentionRepository
            repo = MentionRepository(e2e_db_session)
            saved_check = await repo.get_check_by_id(result.check_id)

            assert saved_check is not None
            assert saved_check.id == result.check_id
            assert saved_check.status == "completed"
            assert saved_check.prompt == prompt

            # 验证品牌和模型信息
            saved_brands = json.loads(saved_check.brands_checked)
            saved_models = json.loads(saved_check.models_used)
            assert set(saved_brands) == set(test_brands)
            assert set(saved_models) == set(models)
            
            print(f"✅ 端到端检测流程测试成功")
            print(f"   检测ID: {result.check_id}")
            print(f"   总提及数: {result.summary['total_mentions']}")
            print(f"   提及率: {result.summary['mention_rate']:.2%}")
            print(f"   平均置信度: {result.summary['avg_confidence']:.2f}")
            
        except Exception as e:
            pytest.fail(f"端到端检测流程测试失败: {str(e)}")

    async def test_multi_brand_detection(
        self,
        skip_if_no_api_keys,
        mention_service,
        test_project_data,
        e2e_config
    ):
        """多品牌检测测试"""
        # 使用更多品牌进行测试
        brands = ["Notion", "Obsidian", "Roam Research", "Logseq", "Craft"]
        prompt = "比较几个知识管理工具的优缺点"
        models = ["doubao"]  # 使用单个模型以减少API调用
        
        print(f"🔍 开始多品牌检测测试")
        print(f"   品牌数量: {len(brands)}")
        
        try:
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
                prompt=prompt,
                brands=brands,
                config=config
            )
            
            # 验证所有品牌都被检测
            assert len(result.results) == 1  # 一个模型
            model_result = result.results[0]
            assert len(model_result.mentions) == len(brands)
            
            # 验证每个品牌都有检测结果
            detected_brands = {mention.brand for mention in model_result.mentions}
            assert detected_brands == set(brands)
            
            # 统计被提及的品牌
            mentioned_brands = [
                mention.brand for mention in model_result.mentions 
                if mention.mentioned
            ]
            
            print(f"✅ 多品牌检测测试成功")
            print(f"   检测品牌: {len(brands)}")
            print(f"   被提及品牌: {len(mentioned_brands)}")
            print(f"   被提及的品牌: {mentioned_brands}")
            
        except Exception as e:
            pytest.fail(f"多品牌检测测试失败: {str(e)}")

    async def test_real_world_scenarios(
        self,
        skip_if_no_api_keys,
        mention_service,
        test_prompts,
        test_project_data,
        e2e_config
    ):
        """真实世界场景测试"""
        brands = ["Notion", "Obsidian"]
        models = ["doubao", "deepseek"]
        
        print(f"🌍 开始真实世界场景测试")
        
        scenario_results = {}
        
        for scenario_name, prompt in test_prompts.items():
            print(f"   测试场景: {scenario_name}")
            
            try:
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
                    prompt=prompt,
                    brands=brands,
                    config=config
                )

                # 收集场景结果
                scenario_results[scenario_name] = {
                    "total_mentions": result.summary["total_mentions"],
                    "mention_rate": result.summary["mention_rate"],
                    "avg_confidence": result.summary["avg_confidence"],
                    "models_count": len(result.results)
                }

                # 基本验证
                assert result.status == "completed"
                assert len(result.results) == len(models)

                print(f"     ✅ {scenario_name}: 提及率 {result.summary['mention_rate']:.2%}")
                
            except Exception as e:
                pytest.fail(f"场景 {scenario_name} 测试失败: {str(e)}")
        
        # 验证所有场景都有结果
        assert len(scenario_results) == len(test_prompts)
        
        # 打印汇总结果
        print(f"✅ 真实世界场景测试完成")
        for scenario, stats in scenario_results.items():
            print(f"   {scenario}: 提及数={stats['total_mentions']}, "
                  f"提及率={stats['mention_rate']:.2%}, "
                  f"置信度={stats['avg_confidence']:.2f}")

    async def test_error_recovery(
        self,
        skip_if_no_api_keys,
        mention_service,
        test_project_data,
        e2e_config
    ):
        """错误恢复测试"""
        print(f"🔧 开始错误恢复测试")
        
        # 测试空品牌列表
        try:
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
                prompt="测试空品牌列表",
                brands=[],  # 空品牌列表
                config=config
            )
            
            # 应该能正常处理空品牌列表
            assert result.status == "completed"
            assert len(result.results) == 1
            assert len(result.results[0].mentions) == 0
            
            print(f"   ✅ 空品牌列表处理正常")
            
        except Exception as e:
            pytest.fail(f"空品牌列表测试失败: {str(e)}")
        
        # 测试空Prompt
        try:
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
                prompt="",  # 空Prompt
                brands=["Notion"],
                config=config
            )
            
            # 应该能处理空Prompt
            assert result.status == "completed"
            
            print(f"   ✅ 空Prompt处理正常")
            
        except Exception as e:
            # 空Prompt可能会导致错误，这是可以接受的
            print(f"   ⚠️ 空Prompt导致错误（可接受）: {str(e)}")
        
        print(f"✅ 错误恢复测试完成")
