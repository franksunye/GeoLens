"""
引用检测数据库集成测试

测试SQLite数据库集成和Repository层功能。
"""

import pytest
import json
import uuid
from datetime import datetime
from app.repositories.mention_repository import MentionRepository
from app.models.mention import MentionCheck, MentionResult, BrandMention, PromptTemplate


class TestMentionRepository:
    """测试引用检测Repository"""
    
    @pytest.mark.asyncio
    async def test_create_and_get_check(self, async_db_session):
        """测试创建和获取检测记录"""
        repo = MentionRepository(async_db_session)

        check_id = str(uuid.uuid4())
        check_data = {
            "id": check_id,
            "project_id": "test-project",
            "user_id": "test-user",
            "prompt": "推荐协作工具",
            "brands_checked": json.dumps(["Notion", "Obsidian"]),
            "models_used": json.dumps(["doubao", "deepseek"]),
            "status": "pending"
        }
        
        # 创建检测记录
        check = await repo.create_check(check_data)
        assert check.id == check_id
        assert check.project_id == "test-project"
        assert check.status == "pending"

        # 获取检测记录
        retrieved_check = await repo.get_check_by_id(check_id)
        assert retrieved_check is not None
        assert retrieved_check.id == check_id
        assert retrieved_check.prompt == "推荐协作工具"
    
    @pytest.mark.asyncio
    async def test_save_result_and_mentions(self, async_db_session):
        """测试保存模型结果和品牌提及"""
        repo = MentionRepository(async_db_session)
        
        # 先创建检测记录
        check_id = str(uuid.uuid4())
        check_data = {
            "id": check_id,
            "project_id": "test-project",
            "user_id": "test-user",
            "prompt": "推荐协作工具",
            "brands_checked": json.dumps(["Notion", "Obsidian"]),
            "models_used": json.dumps(["doubao"]),
            "status": "running"
        }
        await repo.create_check(check_data)

        # 保存模型结果
        result_id = str(uuid.uuid4())
        result_data = {
            "id": result_id,
            "check_id": check_id,
            "model": "doubao",
            "response_text": "我推荐Notion作为团队协作工具",
            "processing_time_ms": 1500
        }
        result = await repo.save_result(result_data)
        assert result.id == result_id
        assert result.model == "doubao"

        # 保存品牌提及
        mentions_data = [
            {
                "id": str(uuid.uuid4()),
                "result_id": result_id,
                "brand": "Notion",
                "mentioned": True,
                "confidence_score": 0.95,
                "context_snippet": "我推荐Notion作为团队协作工具",
                "position": 1
            },
            {
                "id": str(uuid.uuid4()),
                "result_id": result_id,
                "brand": "Obsidian",
                "mentioned": False,
                "confidence_score": 0.1,
                "context_snippet": None,
                "position": None
            }
        ]
        mentions = await repo.save_mentions(mentions_data)
        assert len(mentions) == 2
        assert mentions[0].brand == "Notion"
        assert mentions[0].mentioned == True
        assert mentions[1].brand == "Obsidian"
        assert mentions[1].mentioned == False
    
    @pytest.mark.asyncio
    async def test_get_checks_by_project(self, async_db_session):
        """测试按项目获取检测记录"""
        repo = MentionRepository(async_db_session)
        
        # 创建多个检测记录
        project_id = str(uuid.uuid4())
        for i in range(3):
            check_data = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "user_id": "test-user",
                "prompt": f"测试Prompt {i}",
                "brands_checked": json.dumps(["Brand1", "Brand2"]),
                "models_used": json.dumps(["doubao"]),
                "status": "completed"
            }
            await repo.create_check(check_data)
        
        # 获取项目的检测记录
        checks = await repo.get_checks_by_project(project_id, page=1, limit=10)
        assert len(checks) == 3

        # 测试分页
        checks_page1 = await repo.get_checks_by_project(project_id, page=1, limit=2)
        assert len(checks_page1) == 2

        checks_page2 = await repo.get_checks_by_project(project_id, page=2, limit=2)
        assert len(checks_page2) == 1
    
    @pytest.mark.asyncio
    async def test_update_check_status(self, async_db_session):
        """测试更新检测记录状态"""
        repo = MentionRepository(async_db_session)
        
        # 创建检测记录
        check_id = str(uuid.uuid4())
        check_data = {
            "id": check_id,
            "project_id": "test-project",
            "user_id": "test-user",
            "prompt": "测试更新",
            "brands_checked": json.dumps(["Brand1"]),
            "models_used": json.dumps(["doubao"]),
            "status": "running"
        }
        await repo.create_check(check_data)

        # 更新状态
        success = await repo.update_check_status(
            check_id=check_id,
            status="completed",
            completed_at=datetime.now(),
            total_mentions=2,
            mention_rate=0.75,
            avg_confidence=0.92
        )
        assert success == True

        # 验证更新
        updated_check = await repo.get_check_by_id(check_id)
        assert updated_check.status == "completed"
        assert updated_check.total_mentions == 2
        assert updated_check.mention_rate == 0.75
        assert updated_check.avg_confidence == 0.92
    
    @pytest.mark.asyncio
    async def test_save_and_get_template(self, async_db_session):
        """测试保存和获取Prompt模板"""
        repo = MentionRepository(async_db_session)
        
        template_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        template_data = {
            "id": template_id,
            "user_id": user_id,
            "name": "协作工具推荐",
            "category": "productivity",
            "template": "推荐几个适合{team_size}人团队的{tool_type}工具",
            "variables": json.dumps({"team_size": "5-10", "tool_type": "协作"}),
            "description": "团队协作工具推荐模板",
            "usage_count": 0,
            "is_public": False
        }

        # 保存模板
        template = await repo.save_template(template_data)
        assert template.id == template_id
        assert template.name == "协作工具推荐"
        assert template.category == "productivity"
        
        # 获取用户模板
        templates = await repo.get_templates_by_user(user_id, page=1, limit=10)
        assert len(templates) == 1
        assert templates[0].name == "协作工具推荐"

        # 测试分类过滤
        templates_filtered = await repo.get_templates_by_user(
            user_id,
            category="productivity",
            page=1,
            limit=10
        )
        assert len(templates_filtered) == 1

        # 测试不存在的分类
        templates_empty = await repo.get_templates_by_user(
            user_id,
            category="nonexistent",
            page=1,
            limit=10
        )
        assert len(templates_empty) == 0
    
    @pytest.mark.asyncio
    async def test_brand_mention_stats(self, async_db_session):
        """测试品牌提及统计"""
        repo = MentionRepository(async_db_session)
        
        # 创建测试数据
        project_id = str(uuid.uuid4())
        check_id = str(uuid.uuid4())
        result_id = str(uuid.uuid4())

        check_data = {
            "id": check_id,
            "project_id": project_id,
            "user_id": "test-user",
            "prompt": "推荐工具",
            "brands_checked": json.dumps(["TestBrand"]),
            "models_used": json.dumps(["doubao"]),
            "status": "completed"
        }
        await repo.create_check(check_data)

        result_data = {
            "id": result_id,
            "check_id": check_id,
            "model": "doubao",
            "response_text": "推荐TestBrand",
            "processing_time_ms": 1000
        }
        await repo.save_result(result_data)

        mentions_data = [{
            "id": str(uuid.uuid4()),
            "result_id": result_id,
            "brand": "TestBrand",
            "mentioned": True,
            "confidence_score": 0.9,
            "context_snippet": "推荐TestBrand",
            "position": 1
        }]
        await repo.save_mentions(mentions_data)

        # 获取统计数据
        stats = await repo.get_brand_mention_stats(project_id, "TestBrand", days=30)
        assert stats["brand"] == "TestBrand"
        assert stats["total_checks"] == 1
        assert stats["total_mentions"] == 1
        assert stats["mention_rate"] == 1.0
        assert stats["avg_confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_brand_comparison_stats(self, async_db_session):
        """测试品牌对比统计"""
        repo = MentionRepository(async_db_session)
        
        # 创建对比测试数据
        brands = ["BrandA", "BrandB"]
        project_id = str(uuid.uuid4())

        for i, brand in enumerate(brands):
            check_id = str(uuid.uuid4())
            result_id = str(uuid.uuid4())

            check_data = {
                "id": check_id,
                "project_id": project_id,
                "user_id": "test-user",
                "prompt": f"推荐{brand}",
                "brands_checked": json.dumps([brand]),
                "models_used": json.dumps(["doubao"]),
                "status": "completed"
            }
            await repo.create_check(check_data)

            result_data = {
                "id": result_id,
                "check_id": check_id,
                "model": "doubao",
                "response_text": f"推荐{brand}",
                "processing_time_ms": 1000
            }
            await repo.save_result(result_data)

            mentions_data = [{
                "id": str(uuid.uuid4()),
                "result_id": result_id,
                "brand": brand,
                "mentioned": True,
                "confidence_score": 0.8 + i * 0.1,  # BrandA: 0.8, BrandB: 0.9
                "context_snippet": f"推荐{brand}",
                "position": 1
            }]
            await repo.save_mentions(mentions_data)

        # 获取对比统计
        comparison = await repo.get_brand_comparison_stats(project_id, brands, days=30)
        assert len(comparison) == 2
        
        # 验证数据
        brand_a_stats = next(item for item in comparison if item["brand"] == "BrandA")
        brand_b_stats = next(item for item in comparison if item["brand"] == "BrandB")
        
        assert brand_a_stats["mention_rate"] == 1.0
        assert brand_a_stats["avg_confidence"] == 0.8
        assert brand_b_stats["mention_rate"] == 1.0
        assert brand_b_stats["avg_confidence"] == 0.9
