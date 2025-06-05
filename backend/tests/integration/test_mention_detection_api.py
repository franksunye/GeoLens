"""
引用检测API集成测试

测试引用检测API的完整功能。
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.core.deps import get_current_user
from app.models.user import User


# 创建测试用户
def create_test_user():
    return User(
        id="test-user-id",
        email="test@example.com",
        full_name="Test User",
        password_hash="test-hash",
        is_active=True
    )


# Override dependency
app.dependency_overrides[get_current_user] = create_test_user

client = TestClient(app)


class TestMentionDetectionAPI:
    """引用检测API测试"""
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/api/v1/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert "timestamp" in data
        assert "version" in data
    
    @patch('app.services.mention_detection.MentionDetectionService.check_mentions')
    def test_check_mention_success(self, mock_check_mentions):
        """测试成功的引用检测"""
        # Mock服务响应
        mock_check_mentions.return_value = {
            "check_id": "test-check-id",
            "project_id": "test-project",
            "prompt": "推荐团队协作工具",
            "status": "completed",
            "results": [
                {
                    "model": "doubao",
                    "response_text": "我推荐使用Notion作为团队协作工具。",
                    "mentions": [
                        {
                            "brand": "Notion",
                            "mentioned": True,
                            "confidence_score": 0.95,
                            "context_snippet": "推荐使用Notion作为团队协作工具",
                            "position": 1
                        }
                    ],
                    "processing_time_ms": 1500
                }
            ],
            "summary": {
                "total_mentions": 1,
                "brands_mentioned": ["Notion"],
                "mention_rate": 0.5,
                "avg_confidence": 0.95
            },
            "created_at": "2024-06-03T10:00:00",
            "completed_at": "2024-06-03T10:02:00"
        }
        
        response = client.post(
            "/api/v1/api/check-mention",
            json={
                "project_id": "test-project",
                "prompt": "推荐团队协作工具",
                "brands": ["Notion", "Obsidian"],
                "models": ["doubao", "deepseek"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert len(data["results"]) >= 1
        assert data["summary"]["total_mentions"] >= 0
    
    def test_check_mention_missing_fields(self):
        """测试缺少必需字段的请求"""
        response = client.post(
            "/api/v1/api/check-mention",
            json={
                "project_id": "test-project",
                # 缺少prompt和brands
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_check_mention_empty_brands(self):
        """测试空品牌列表"""
        response = client.post(
            "/api/v1/api/check-mention",
            json={
                "project_id": "test-project",
                "prompt": "推荐团队协作工具",
                "brands": [],  # 空列表
                "models": ["doubao"]
            }
        )
        
        assert response.status_code == 200  # 应该能处理空列表
    
    @patch('app.services.mention_detection.MentionDetectionService.get_history')
    def test_get_history_success(self, mock_get_history):
        """测试获取历史记录"""
        # Mock服务响应
        mock_get_history.return_value = {
            "checks": [
                {
                    "id": "check-1",
                    "prompt": "推荐团队协作工具",
                    "brands_checked": ["Notion", "Obsidian"],
                    "models_used": ["doubao", "deepseek"],
                    "total_mentions": 2,
                    "mention_rate": 0.75,
                    "created_at": "2024-06-03T10:00:00"
                }
            ],
            "pagination": {
                "page": 1,
                "limit": 20,
                "total": 1,
                "pages": 1
            }
        }
        
        response = client.get(
            "/api/v1/api/get-history",
            params={"project_id": "test-project"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "checks" in data
        assert "pagination" in data
    
    def test_get_history_missing_project_id(self):
        """测试缺少项目ID的历史查询"""
        response = client.get("/api/v1/api/get-history")
        
        assert response.status_code == 422  # Missing required parameter
    
    def test_get_history_with_filters(self):
        """测试带过滤器的历史查询"""
        response = client.get(
            "/api/v1/api/get-history",
            params={
                "project_id": "test-project",
                "brand": "Notion",
                "model": "doubao",
                "page": 1,
                "limit": 10
            }
        )
        
        assert response.status_code == 200
    
    @patch('app.services.mention_detection.MentionDetectionService.save_prompt_template')
    def test_save_prompt_success(self, mock_save_prompt):
        """测试保存Prompt模板"""
        # Mock服务响应
        mock_save_prompt.return_value = {
            "id": "template-id",
            "name": "协作工具推荐",
            "category": "productivity",
            "template": "推荐{count}个{type}工具",
            "variables": {"count": "string", "type": "string"},
            "usage_count": 0,
            "created_at": "2024-06-03T10:00:00"
        }
        
        response = client.post(
            "/api/v1/api/save-prompt",
            json={
                "name": "协作工具推荐",
                "category": "productivity",
                "template": "推荐{count}个{type}工具",
                "variables": {"count": "string", "type": "string"},
                "description": "用于推荐协作工具的模板"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "协作工具推荐"
        assert data["category"] == "productivity"
    
    def test_save_prompt_missing_fields(self):
        """测试缺少必需字段的模板保存"""
        response = client.post(
            "/api/v1/api/save-prompt",
            json={
                "name": "测试模板",
                # 缺少category和template
            }
        )
        
        assert response.status_code == 422
    
    @patch('app.services.mention_detection.MentionDetectionService.get_prompt_templates')
    def test_get_prompt_templates(self, mock_get_templates):
        """测试获取Prompt模板列表"""
        # Mock服务响应
        mock_get_templates.return_value = {
            "templates": [
                {
                    "id": "template-1",
                    "name": "协作工具推荐",
                    "category": "productivity",
                    "template": "推荐{count}个{type}工具",
                    "usage_count": 25,
                    "created_at": "2024-06-03T10:00:00"
                }
            ],
            "pagination": {
                "page": 1,
                "limit": 10,
                "total": 1,
                "pages": 1
            }
        }
        
        response = client.get("/api/v1/api/prompts/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "pagination" in data
    
    def test_get_prompt_templates_with_category(self):
        """测试按分类获取模板"""
        response = client.get(
            "/api/v1/api/prompts/templates",
            params={"category": "productivity", "page": 1, "limit": 5}
        )
        
        assert response.status_code == 200
    
    @patch('app.services.mention_detection.MentionDetectionService.get_mention_analytics')
    def test_get_mention_analytics(self, mock_get_analytics):
        """测试获取引用统计"""
        # Mock服务响应
        mock_get_analytics.return_value = {
            "brand": "Notion",
            "timeframe": "30d",
            "total_checks": 45,
            "total_mentions": 32,
            "mention_rate": 0.71,
            "model_performance": {
                "doubao": {"checks": 20, "mentions": 15, "rate": 0.75},
                "deepseek": {"checks": 15, "mentions": 10, "rate": 0.67}
            },
            "trend_data": [
                {"date": "2024-05-01", "mentions": 5, "checks": 7}
            ]
        }
        
        response = client.get(
            "/api/v1/api/analytics/mentions",
            params={"project_id": "test-project", "brand": "Notion"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["brand"] == "Notion"
        assert "total_checks" in data
        assert "mention_rate" in data
    
    def test_get_mention_analytics_missing_project_id(self):
        """测试缺少项目ID的统计查询"""
        response = client.get("/api/v1/api/analytics/mentions")
        
        assert response.status_code == 422
    
    @patch('app.services.mention_detection.MentionDetectionService.compare_brands')
    def test_compare_brands(self, mock_compare_brands):
        """测试竞品对比分析"""
        # Mock服务响应
        mock_compare_brands.return_value = {
            "comparison": [
                {"brand": "Notion", "mention_rate": 0.75, "avg_confidence": 0.92},
                {"brand": "Obsidian", "mention_rate": 0.60, "avg_confidence": 0.85}
            ],
            "insights": ["Notion在团队协作场景中被提及最多"]
        }
        
        response = client.get(
            "/api/v1/api/analytics/compare",
            params={
                "project_id": "test-project",
                "brands": "Notion,Obsidian,Roam Research"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "comparison" in data
        assert "insights" in data
        assert len(data["comparison"]) >= 2
    
    def test_compare_brands_missing_params(self):
        """测试缺少参数的竞品对比"""
        response = client.get("/api/v1/api/analytics/compare")
        
        assert response.status_code == 422


class TestMentionDetectionAPIErrorHandling:
    """引用检测API错误处理测试"""
    
    @patch('app.services.mention_detection.MentionDetectionService.check_mentions')
    def test_check_mention_service_error(self, mock_check_mentions):
        """测试服务层错误处理"""
        # Mock服务抛出异常
        mock_check_mentions.side_effect = Exception("Service error")
        
        response = client.post(
            "/api/v1/api/check-mention",
            json={
                "project_id": "test-project",
                "prompt": "推荐团队协作工具",
                "brands": ["Notion"],
                "models": ["doubao"]
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        # 检查错误响应格式
        assert "error" in data
        assert data["error"]["code"] == "HTTP_500"
        assert "Mention detection failed" in data["error"]["message"]
    
    @patch('app.services.mention_detection.MentionDetectionService.get_history')
    def test_get_history_service_error(self, mock_get_history):
        """测试历史查询服务错误"""
        mock_get_history.side_effect = Exception("Database error")
        
        response = client.get(
            "/api/v1/api/get-history",
            params={"project_id": "test-project"}
        )
        
        assert response.status_code == 500
        data = response.json()
        # 检查错误响应格式
        assert "error" in data
        assert data["error"]["code"] == "HTTP_500"
        assert "Failed to get history" in data["error"]["message"]
    
    def test_invalid_json_request(self):
        """测试无效JSON请求"""
        response = client.post(
            "/api/v1/api/check-mention",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_unauthorized_request(self):
        """测试未授权请求"""
        # 临时移除用户依赖覆盖
        del app.dependency_overrides[get_current_user]
        
        response = client.post(
            "/api/v1/api/check-mention",
            json={
                "project_id": "test-project",
                "prompt": "test",
                "brands": ["test"],
                "models": ["doubao"]
            }
        )
        
        # 应该返回401或403
        assert response.status_code in [401, 403]
        
        # 恢复依赖覆盖
        app.dependency_overrides[get_current_user] = create_test_user


class TestMentionDetectionAPIPerformance:
    """引用检测API性能测试"""
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        import concurrent.futures
        import time
        
        def make_request():
            return client.get(
                "/api/v1/api/get-history",
                params={"project_id": "test-project"}
            )
        
        start_time = time.time()
        
        # 发送10个并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        end_time = time.time()
        
        # 检查所有请求都成功
        for response in responses:
            assert response.status_code == 200
        
        # 检查响应时间合理（应该在5秒内完成）
        assert end_time - start_time < 5.0
    
    def test_large_brand_list(self):
        """测试大量品牌列表的处理"""
        # 创建100个品牌的列表
        large_brand_list = [f"Brand{i}" for i in range(100)]
        
        response = client.post(
            "/api/v1/api/check-mention",
            json={
                "project_id": "test-project",
                "prompt": "推荐工具",
                "brands": large_brand_list,
                "models": ["doubao"]
            }
        )
        
        # 应该能处理大量品牌（可能会有性能限制）
        assert response.status_code in [200, 400, 422]
