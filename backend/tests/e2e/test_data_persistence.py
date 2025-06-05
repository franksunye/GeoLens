"""
真实场景下的数据持久化测试
"""

import pytest
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.services.mention_detection import MentionDetectionService
from app.repositories.mention_repository import MentionRepository
from app.repositories.prompt_repository import PromptRepository


@pytest.mark.e2e
class TestDataPersistence:
    """测试真实场景下的数据持久化"""

    async def test_detection_history_persistence(
        self, 
        skip_if_no_api_keys, 
        mention_service, 
        test_project_data,
        e2e_db_session
    ):
        """检测历史持久化测试"""
        print(f"💾 开始检测历史持久化测试")
        
        # 执行多次检测以创建历史记录
        test_cases = [
            {
                "prompt": "推荐笔记软件",
                "brands": ["Notion", "Obsidian"],
                "models": ["doubao"]
            },
            {
                "prompt": "团队协作工具有哪些？",
                "brands": ["Notion", "Slack"],
                "models": ["deepseek"]
            },
            {
                "prompt": "知识管理系统推荐",
                "brands": ["Roam Research", "Logseq"],
                "models": ["doubao"]
            }
        ]
        
        check_ids = []
        
        # 执行检测并收集ID
        for i, test_case in enumerate(test_cases):
            print(f"   执行检测 {i+1}/{len(test_cases)}")
            
            result = await mention_service.check_mentions(
                prompt=test_case["prompt"],
                brands=test_case["brands"],
                models=test_case["models"],
                project_id=test_project_data["project_id"],
                user_id=test_project_data["user_id"]
            )
            
            assert result.status == "completed"
            check_ids.append(result.check_id)
        
        # 验证数据库中的历史记录
        repo = MentionRepository(e2e_db_session)
        
        # 获取项目的所有检测历史
        history = await repo.get_checks_by_project(
            project_id=test_project_data["project_id"],
            limit=10
        )
        
        # 验证历史记录数量
        assert len(history) >= len(test_cases)
        
        # 验证每个检测记录的完整性
        for check_id in check_ids:
            saved_check = await repo.get_check_by_id(check_id)
            
            assert saved_check is not None
            assert saved_check["id"] == check_id
            assert saved_check["status"] == "completed"
            assert saved_check["project_id"] == test_project_data["project_id"]
            assert saved_check["user_id"] == test_project_data["user_id"]
            
            # 验证JSON字段
            brands_checked = json.loads(saved_check["brands_checked"])
            models_used = json.loads(saved_check["models_used"])
            
            assert isinstance(brands_checked, list)
            assert isinstance(models_used, list)
            assert len(brands_checked) > 0
            assert len(models_used) > 0
            
            # 验证时间戳
            assert saved_check["created_at"] is not None
            assert saved_check["updated_at"] is not None
        
        print(f"✅ 检测历史持久化测试成功")
        print(f"   创建检测记录: {len(check_ids)}")
        print(f"   历史记录总数: {len(history)}")

    async def test_prompt_template_persistence(
        self, 
        skip_if_no_api_keys, 
        test_project_data,
        e2e_db_session
    ):
        """Prompt模板持久化测试"""
        print(f"📝 开始Prompt模板持久化测试")
        
        repo = PromptRepository(e2e_db_session)
        
        # 创建测试模板
        test_templates = [
            {
                "name": "E2E测试模板1",
                "category": "协作工具",
                "template": "推荐几个适合{team_size}人团队的{tool_type}工具",
                "variables": {"team_size": "小型", "tool_type": "协作"},
                "user_id": test_project_data["user_id"]
            },
            {
                "name": "E2E测试模板2", 
                "category": "生产力工具",
                "template": "有哪些{platform}平台上的{category}应用推荐？",
                "variables": {"platform": "移动端", "category": "笔记"},
                "user_id": test_project_data["user_id"]
            }
        ]
        
        template_ids = []
        
        # 保存模板
        for template_data in test_templates:
            template_id = await repo.save_prompt_template(
                name=template_data["name"],
                category=template_data["category"],
                template=template_data["template"],
                variables=template_data["variables"],
                user_id=template_data["user_id"]
            )
            
            assert template_id is not None
            template_ids.append(template_id)
        
        # 验证模板保存
        for i, template_id in enumerate(template_ids):
            saved_template = await repo.get_prompt_template(template_id)
            
            assert saved_template is not None
            assert saved_template["id"] == template_id
            assert saved_template["name"] == test_templates[i]["name"]
            assert saved_template["category"] == test_templates[i]["category"]
            assert saved_template["template"] == test_templates[i]["template"]
            
            # 验证variables字段
            saved_variables = json.loads(saved_template["variables"])
            assert saved_variables == test_templates[i]["variables"]
            
            # 验证使用计数
            assert saved_template["usage_count"] == 0
        
        # 测试模板使用计数更新
        await repo.increment_template_usage(template_ids[0])
        updated_template = await repo.get_prompt_template(template_ids[0])
        assert updated_template["usage_count"] == 1
        
        # 获取用户的所有模板
        user_templates = await repo.get_user_templates(test_project_data["user_id"])
        user_template_ids = [t["id"] for t in user_templates]
        
        for template_id in template_ids:
            assert template_id in user_template_ids
        
        print(f"✅ Prompt模板持久化测试成功")
        print(f"   创建模板数: {len(template_ids)}")
        print(f"   用户模板总数: {len(user_templates)}")

    async def test_data_integrity_across_operations(
        self, 
        skip_if_no_api_keys, 
        mention_service,
        test_project_data,
        e2e_db_session
    ):
        """跨操作数据完整性测试"""
        print(f"🔒 开始数据完整性测试")
        
        # 1. 创建检测记录
        result = await mention_service.check_mentions(
            prompt="数据完整性测试",
            brands=["Notion", "Obsidian"],
            models=["doubao"],
            project_id=test_project_data["project_id"],
            user_id=test_project_data["user_id"]
        )
        
        check_id = result.check_id
        
        # 2. 验证初始数据
        mention_repo = MentionRepository(e2e_db_session)
        initial_check = await mention_repo.get_check_by_id(check_id)
        
        assert initial_check is not None
        initial_created_at = initial_check["created_at"]
        initial_updated_at = initial_check["updated_at"]
        
        # 3. 获取检测历史（应该包含新记录）
        history = await mention_repo.get_checks_by_project(
            project_id=test_project_data["project_id"],
            limit=5
        )
        
        check_ids_in_history = [check["id"] for check in history]
        assert check_id in check_ids_in_history
        
        # 4. 验证数据在不同查询中的一致性
        check_by_id = await mention_repo.get_check_by_id(check_id)
        check_in_history = next(
            (check for check in history if check["id"] == check_id), 
            None
        )
        
        assert check_in_history is not None
        
        # 验证关键字段一致性
        assert check_by_id["prompt"] == check_in_history["prompt"]
        assert check_by_id["status"] == check_in_history["status"]
        assert check_by_id["project_id"] == check_in_history["project_id"]
        assert check_by_id["user_id"] == check_in_history["user_id"]
        
        # 5. 验证时间戳的合理性
        now = datetime.utcnow()
        created_at = datetime.fromisoformat(initial_created_at.replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(initial_updated_at.replace('Z', '+00:00'))
        
        # 创建时间应该在合理范围内（最近5分钟）
        assert (now - created_at) < timedelta(minutes=5)
        assert (now - updated_at) < timedelta(minutes=5)
        
        # 更新时间应该不早于创建时间
        assert updated_at >= created_at
        
        print(f"✅ 数据完整性测试成功")
        print(f"   检测ID: {check_id}")
        print(f"   创建时间: {created_at}")
        print(f"   更新时间: {updated_at}")

    async def test_concurrent_data_operations(
        self, 
        skip_if_no_api_keys, 
        mention_service,
        test_project_data,
        e2e_db_session
    ):
        """并发数据操作测试"""
        print(f"⚡ 开始并发数据操作测试")
        
        import asyncio
        
        # 准备并发检测任务
        async def run_detection(prompt_suffix: str):
            return await mention_service.check_mentions(
                prompt=f"并发测试 {prompt_suffix}",
                brands=["Notion"],
                models=["doubao"],
                project_id=test_project_data["project_id"],
                user_id=test_project_data["user_id"]
            )
        
        # 执行并发检测
        tasks = [
            run_detection("任务1"),
            run_detection("任务2"),
            run_detection("任务3")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证结果
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   ❌ 任务 {i+1} 失败: {str(result)}")
            else:
                assert result.status == "completed"
                successful_results.append(result)
                print(f"   ✅ 任务 {i+1} 成功: {result.check_id}")
        
        # 至少要有一个成功
        assert len(successful_results) > 0
        
        # 验证所有成功的检测都被正确保存
        mention_repo = MentionRepository(e2e_db_session)
        
        for result in successful_results:
            saved_check = await mention_repo.get_check_by_id(result.check_id)
            assert saved_check is not None
            assert saved_check["status"] == "completed"
        
        print(f"✅ 并发数据操作测试成功")
        print(f"   并发任务数: {len(tasks)}")
        print(f"   成功任务数: {len(successful_results)}")
