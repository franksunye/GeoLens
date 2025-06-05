"""
引用检测模块测试

测试引用检测的核心功能。
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.services.mention_detection import MentionDetectionService
from app.api.v1.mention_detection import BrandMention, ModelResult


class TestMentionDetectionService:
    """引用检测服务测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.service = MentionDetectionService()
    
    def test_service_initialization(self):
        """测试服务初始化"""
        assert self.service is not None
        assert hasattr(self.service, 'ai_factory')
        assert hasattr(self.service, 'checks_storage')
        assert hasattr(self.service, 'templates_storage')
    
    def test_analyze_mentions_exact_match(self):
        """测试精确匹配的品牌提及分析"""
        text = "我推荐使用Notion作为团队协作工具，它功能强大且易用。"
        brands = ["Notion", "Obsidian"]
        
        mentions = self.service._analyze_mentions(text, brands)
        
        assert len(mentions) == 2
        
        # 检查Notion被正确识别
        notion_mention = next(m for m in mentions if m.brand == "Notion")
        assert notion_mention.mentioned is True
        assert notion_mention.confidence_score > 0.8
        assert "推荐使用Notion作为团队协作工具" in notion_mention.context_snippet
        assert notion_mention.position == 1
        
        # 检查Obsidian未被提及
        obsidian_mention = next(m for m in mentions if m.brand == "Obsidian")
        assert obsidian_mention.mentioned is False
        assert obsidian_mention.confidence_score == 0.0
        assert obsidian_mention.context_snippet is None
    
    def test_analyze_mentions_multiple_brands(self):
        """测试多品牌提及分析"""
        text = "对于知识管理，我建议考虑Notion、Obsidian和Roam Research这三个工具。"
        brands = ["Notion", "Obsidian", "Roam Research"]
        
        mentions = self.service._analyze_mentions(text, brands)
        
        assert len(mentions) == 3
        
        # 所有品牌都应该被识别
        for mention in mentions:
            assert mention.mentioned is True
            assert mention.confidence_score > 0.8
            assert mention.position is not None
        
        # 检查位置排序
        positions = [m.position for m in mentions if m.mentioned]
        assert sorted(positions) == [1, 2, 3]
    
    def test_analyze_mentions_case_insensitive(self):
        """测试大小写不敏感的匹配"""
        text = "我觉得notion是个不错的选择。"
        brands = ["Notion"]
        
        mentions = self.service._analyze_mentions(text, brands)
        
        assert len(mentions) == 1
        assert mentions[0].mentioned is True
        assert mentions[0].confidence_score > 0.8
    
    def test_calculate_confidence_positive_context(self):
        """测试正面上下文的置信度计算"""
        text = "我强烈推荐使用Notion，它是一个优秀的工具。"
        brand = "Notion"
        position = text.lower().find(brand.lower())
        
        confidence = self.service._calculate_confidence(text, brand, position)
        
        # 应该有正面词汇加分
        assert confidence > 0.85
    
    def test_calculate_confidence_negative_context(self):
        """测试负面上下文的置信度计算"""
        text = "我不推荐使用Notion，因为它有一些问题。"
        brand = "Notion"
        position = text.lower().find(brand.lower())
        
        confidence = self.service._calculate_confidence(text, brand, position)
        
        # 应该有负面词汇减分
        assert confidence < 0.85
    
    def test_calculate_position(self):
        """测试品牌位置计算"""
        text = "推荐使用asana、trello和notion这些工具。"
        brands = ["Asana", "Trello", "Notion"]
        
        # 测试每个品牌的位置
        asana_pos = self.service._calculate_position(text, "asana", brands)
        trello_pos = self.service._calculate_position(text, "trello", brands)
        notion_pos = self.service._calculate_position(text, "notion", brands)
        
        assert asana_pos == 1
        assert trello_pos == 2
        assert notion_pos == 3
    
    def test_calculate_position_not_mentioned(self):
        """测试未提及品牌的位置计算"""
        text = "推荐使用asana和trello。"
        brands = ["Asana", "Trello", "Notion"]
        
        notion_pos = self.service._calculate_position(text, "notion", brands)
        
        assert notion_pos is None
    
    @pytest.mark.asyncio
    @patch('app.services.mention_detection.AsyncSessionLocal')
    @patch('app.services.mention_detection.MentionRepository')
    async def test_check_mentions_success(self, mock_repo_class, mock_session_class):
        """测试成功的引用检测"""
        # Mock数据库会话和Repository
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        # Mock AI服务响应
        with patch.object(self.service, '_check_single_model') as mock_check_model:

            mock_check_model.side_effect = [
                ModelResult(
                    model="doubao",
                    response_text="我推荐使用Notion作为团队协作工具。",
                    mentions=[BrandMention(brand="Notion", mentioned=True, confidence_score=0.95)],
                    processing_time_ms=1500
                ),
                ModelResult(
                    model="deepseek",
                    response_text="Notion和Obsidian都是不错的选择。",
                    mentions=[
                        BrandMention(brand="Notion", mentioned=True, confidence_score=0.90),
                        BrandMention(brand="Obsidian", mentioned=True, confidence_score=0.88)
                    ],
                    processing_time_ms=1200
                )
            ]

            result = await self.service.check_mentions(
                prompt="推荐团队协作工具",
                brands=["Notion", "Obsidian"],
                models=["doubao", "deepseek"],
                project_id="test-project",
                user_id="test-user"
            )

            assert result.status == "completed"
            assert len(result.results) == 2
            # 验证结果包含了Mock的数据
            assert result.results[0].model == "doubao"
            assert result.results[1].model == "deepseek"
            # 由于是Mock数据，summary可能为空，这里只验证结构
            assert "total_mentions" in result.summary
            assert "mention_rate" in result.summary
    
    @pytest.mark.asyncio
    @patch('app.services.mention_detection.AsyncSessionLocal')
    @patch('app.services.mention_detection.MentionRepository')
    async def test_check_mentions_with_error(self, mock_repo_class, mock_session_class):
        """测试AI服务出错时的处理"""
        # Mock数据库会话和Repository
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        with patch.object(self.service, '_check_single_model') as mock_check_model:
            mock_check_model.side_effect = Exception("API Error")

            result = await self.service.check_mentions(
                prompt="推荐团队协作工具",
                brands=["Notion"],
                models=["doubao"],
                project_id="test-project",
                user_id="test-user"
            )

            assert result.status == "completed"
            assert len(result.results) == 1
            assert "Error" in result.results[0].response_text
    
    @pytest.mark.asyncio
    @patch('app.services.mention_detection.AsyncSessionLocal')
    @patch('app.services.mention_detection.MentionRepository')
    async def test_get_history(self, mock_repo_class, mock_session_class):
        """测试获取历史记录 - 完全Mock化"""
        # Mock数据库会话和Repository
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        # Mock Repository返回的数据
        mock_repo.get_checks_by_project.return_value = []
        mock_repo.get_checks_count_by_project.return_value = 0

        history = await self.service.get_history(
            project_id="test-project",
            page=1,
            limit=10
        )

        assert "checks" in history.dict()
        assert "pagination" in history.dict()
        assert history.pagination["page"] == 1
        assert history.pagination["limit"] == 10
    
    @pytest.mark.asyncio
    @patch('app.services.mention_detection.AsyncSessionLocal')
    @patch('app.services.mention_detection.MentionRepository')
    async def test_get_history_with_filters(self, mock_repo_class, mock_session_class):
        """测试带过滤器的历史记录查询 - 完全Mock化"""
        # Mock数据库会话和Repository
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        # Mock Repository返回的数据
        mock_repo.get_checks_by_project.return_value = []
        mock_repo.get_checks_count_by_project.return_value = 0

        history = await self.service.get_history(
            project_id="test-project",
            page=1,
            limit=10,
            brand_filter="Notion",
            model_filter="doubao"
        )

        assert "checks" in history.dict()
        # 验证过滤器参数被正确传递
        mock_repo.get_checks_by_project.assert_called_once_with(
            project_id="test-project",
            page=1,
            limit=10,
            brand_filter="Notion",
            model_filter="doubao"
        )
    
    @pytest.mark.asyncio
    @patch('app.services.mention_detection.AsyncSessionLocal')
    @patch('app.services.mention_detection.MentionRepository')
    async def test_save_prompt_template(self, mock_repo_class, mock_session_class):
        """测试保存Prompt模板 - 完全Mock化"""
        # Mock数据库会话和Repository
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        # Mock Repository返回的模板对象
        from app.api.v1.mention_detection import SavePromptResponse
        mock_template = SavePromptResponse(
            id="template-123",
            name="测试模板",
            category="test",
            template="推荐{count}个{type}工具",
            variables={"count": "string", "type": "string"},
            usage_count=0,
            created_at=datetime.now()
        )
        mock_repo.save_template.return_value = mock_template

        template = await self.service.save_prompt_template(
            name="测试模板",
            category="test",
            template="推荐{count}个{type}工具",
            variables={"count": "string", "type": "string"},
            description="测试用模板",
            user_id="test-user"
        )

        assert template.name == "测试模板"
        assert template.category == "test"
        assert template.template == "推荐{count}个{type}工具"
        assert template.usage_count == 0
    
    @pytest.mark.asyncio
    @patch('app.services.mention_detection.AsyncSessionLocal')
    @patch('app.services.mention_detection.MentionRepository')
    async def test_get_prompt_templates(self, mock_repo_class, mock_session_class):
        """测试获取Prompt模板列表 - 完全Mock化"""
        # Mock数据库会话和Repository
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        # Mock Repository返回的数据
        mock_repo.get_templates.return_value = ([], 0)

        templates = await self.service.get_prompt_templates(
            category="productivity",
            page=1,
            limit=10,
            user_id="test-user"
        )

        assert "templates" in templates
        assert "pagination" in templates
        assert templates["pagination"]["page"] == 1
        assert templates["pagination"]["limit"] == 10
    
    @pytest.mark.asyncio
    @patch('app.services.mention_detection.AsyncSessionLocal')
    @patch('app.services.mention_detection.MentionRepository')
    async def test_get_mention_analytics(self, mock_repo_class, mock_session_class):
        """测试获取引用统计 - 完全Mock化"""
        # Mock数据库会话和Repository
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        # Mock Repository返回的统计数据
        mock_repo.get_brand_mention_stats.return_value = {
            "total_checks": 10,
            "total_mentions": 7,
            "mention_rate": 0.7,
            "avg_confidence": 0.85,
            "model_performance": {},
            "trend_data": []
        }

        analytics = await self.service.get_mention_analytics(
            project_id="test-project",
            brand="Notion",
            timeframe="30d"
        )

        assert "brand" in analytics
        assert "timeframe" in analytics
        assert "total_checks" in analytics
        assert "total_mentions" in analytics
        assert "mention_rate" in analytics
        assert "model_performance" in analytics
        assert "trend_data" in analytics
    
    @pytest.mark.asyncio
    @patch('app.services.mention_detection.AsyncSessionLocal')
    @patch('app.services.mention_detection.MentionRepository')
    async def test_compare_brands(self, mock_repo_class, mock_session_class):
        """测试竞品对比分析 - 完全Mock化"""
        # Mock数据库会话和Repository
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        # Mock Repository返回的对比数据
        mock_repo.get_brand_comparison_stats.return_value = [
            {"brand": "Notion", "mention_rate": 0.8, "avg_confidence": 0.9, "total_mentions": 8},
            {"brand": "Obsidian", "mention_rate": 0.6, "avg_confidence": 0.85, "total_mentions": 6},
            {"brand": "Roam Research", "mention_rate": 0.4, "avg_confidence": 0.8, "total_mentions": 4}
        ]

        comparison = await self.service.compare_brands(
            project_id="test-project",
            brands=["Notion", "Obsidian", "Roam Research"]
        )

        assert "comparison" in comparison
        assert "insights" in comparison
        assert len(comparison["comparison"]) == 3

        # 检查对比数据结构
        for brand_data in comparison["comparison"]:
            assert "brand" in brand_data
            assert "mention_rate" in brand_data
            assert "avg_confidence" in brand_data
            assert "total_mentions" in brand_data


class TestBrandMention:
    """品牌提及模型测试"""
    
    def test_brand_mention_creation(self):
        """测试品牌提及对象创建"""
        mention = BrandMention(
            brand="Notion",
            mentioned=True,
            confidence_score=0.95,
            context_snippet="推荐使用Notion作为协作工具",
            position=1
        )
        
        assert mention.brand == "Notion"
        assert mention.mentioned is True
        assert mention.confidence_score == 0.95
        assert mention.context_snippet == "推荐使用Notion作为协作工具"
        assert mention.position == 1
    
    def test_brand_mention_not_mentioned(self):
        """测试未提及的品牌对象"""
        mention = BrandMention(
            brand="Obsidian",
            mentioned=False,
            confidence_score=0.0
        )
        
        assert mention.brand == "Obsidian"
        assert mention.mentioned is False
        assert mention.confidence_score == 0.0
        assert mention.context_snippet is None
        assert mention.position is None


class TestModelResult:
    """模型结果测试"""
    
    def test_model_result_creation(self):
        """测试模型结果对象创建"""
        mentions = [
            BrandMention(brand="Notion", mentioned=True, confidence_score=0.95),
            BrandMention(brand="Obsidian", mentioned=False, confidence_score=0.0)
        ]
        
        result = ModelResult(
            model="doubao",
            response_text="我推荐使用Notion作为团队协作工具。",
            mentions=mentions,
            processing_time_ms=1500
        )
        
        assert result.model == "doubao"
        assert "Notion" in result.response_text
        assert len(result.mentions) == 2
        assert result.processing_time_ms == 1500
    
    def test_model_result_with_error(self):
        """测试包含错误的模型结果"""
        result = ModelResult(
            model="deepseek",
            response_text="Error: API timeout",
            mentions=[],
            processing_time_ms=5000
        )
        
        assert result.model == "deepseek"
        assert "Error" in result.response_text
        assert len(result.mentions) == 0
        assert result.processing_time_ms == 5000
