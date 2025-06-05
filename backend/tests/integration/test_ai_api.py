"""
AI API集成测试
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.ai import AIResponse


class TestAIAPI:
    """AI API集成测试"""
    
    def test_get_ai_providers_unauthenticated(self, client: TestClient):
        """测试未认证用户获取AI提供商列表"""
        response = client.get("/api/v1/ai/providers")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "providers" in data
        assert "default_provider" in data
        assert len(data["providers"]) >= 2  # doubao and deepseek
        
        # 检查提供商信息结构
        for provider in data["providers"]:
            assert "name" in provider
            assert "display_name" in provider
            assert "supported_models" in provider
            assert "available" in provider
            assert "description" in provider
    
    def test_chat_completion_unauthenticated(self, client: TestClient):
        """测试未认证用户聊天完成"""
        response = client.post("/api/v1/ai/chat", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        })

        assert response.status_code == 403
    
    @patch('app.core.config.settings.doubao_api_key', 'test-key')
    @patch('app.services.ai.doubao.DoubaoProvider.chat_completion')
    def test_chat_completion_success(
        self,
        mock_chat_completion,
        authenticated_client: TestClient
    ):
        """测试成功的聊天完成"""
        # 模拟AI响应
        mock_response = AIResponse(
            content="Hello! How can I help you?",
            model="doubao-pro-32k",
            provider="doubao",
            usage={
                "prompt_tokens": 10,
                "completion_tokens": 8,
                "total_tokens": 18
            },
            response_time=1.2,
            metadata={"finish_reason": "stop"}
        )
        mock_chat_completion.return_value = mock_response
        
        response = authenticated_client.post("/api/v1/ai/chat", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "provider": "doubao",
            "temperature": 0.7,
            "max_tokens": 1000
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["content"] == "Hello! How can I help you?"
        assert data["model"] == "doubao-pro-32k"
        assert data["provider"] == "doubao"
        assert data["usage"]["total_tokens"] == 18
        assert data["response_time"] == 1.2
        assert data["metadata"]["finish_reason"] == "stop"
    
    def test_chat_completion_invalid_request(self, authenticated_client: TestClient):
        """测试无效的聊天请求"""
        # 空消息列表
        response = authenticated_client.post("/api/v1/ai/chat", json={
            "messages": []
        })
        assert response.status_code == 422
        
        # 无效角色
        response = authenticated_client.post("/api/v1/ai/chat", json={
            "messages": [
                {"role": "invalid", "content": "Hello"}
            ]
        })
        assert response.status_code == 422
        
        # 空内容
        response = authenticated_client.post("/api/v1/ai/chat", json={
            "messages": [
                {"role": "user", "content": ""}
            ]
        })
        assert response.status_code == 422
    
    def test_chat_completion_no_api_key(self, authenticated_client: TestClient):
        """测试没有API密钥的情况"""
        response = authenticated_client.post("/api/v1/ai/chat", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "provider": "doubao"
        })
        
        assert response.status_code == 500
    
    @patch('app.core.config.settings.doubao_api_key', 'test-key')
    @patch('app.services.ai.doubao.DoubaoProvider.chat_completion_stream')
    def test_chat_completion_stream(
        self,
        mock_stream,
        authenticated_client: TestClient
    ):
        """测试流式聊天完成"""
        # 模拟流式响应
        async def mock_stream_generator():
            yield "Hello"
            yield " there"
            yield "!"
        
        mock_stream.return_value = mock_stream_generator()
        
        response = authenticated_client.post("/api/v1/ai/chat/stream", json={
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "provider": "doubao"
        })
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    @patch('app.core.config.settings.doubao_api_key', 'test-key')
    @patch('app.services.ai.doubao.DoubaoProvider.chat_completion')
    def test_brand_analysis(
        self,
        mock_chat_completion,
        authenticated_client: TestClient
    ):
        """测试品牌分析"""
        # 模拟AI响应
        mock_response = AIResponse(
            content='{"mentions": [], "total_mentions": 0, "overall_sentiment": "neutral", "analysis_summary": "No brand mentions found"}',
            model="doubao-pro-32k",
            provider="doubao",
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            response_time=2.0,
            metadata={}
        )
        mock_chat_completion.return_value = mock_response
        
        response = authenticated_client.post("/api/v1/ai/analyze/brand", json={
            "content": "This is a test article about technology.",
            "brand_keywords": ["Apple", "iPhone"],
            "provider": "doubao",
            "detailed": True
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "mentions" in data
        assert "total_mentions" in data
        assert "overall_sentiment" in data
        assert "analysis_summary" in data
        assert "provider" in data
        assert "processing_time" in data
    
    def test_brand_analysis_invalid_request(self, authenticated_client: TestClient):
        """测试无效的品牌分析请求"""
        # 空内容
        response = authenticated_client.post("/api/v1/ai/analyze/brand", json={
            "content": "",
            "brand_keywords": ["Apple"]
        })
        assert response.status_code == 422
        
        # 空关键词列表
        response = authenticated_client.post("/api/v1/ai/analyze/brand", json={
            "content": "Test content",
            "brand_keywords": []
        })
        assert response.status_code == 422
    
    @patch('app.core.config.settings.doubao_api_key', 'test-key')
    @patch('app.services.ai.doubao.DoubaoProvider.health_check')
    def test_health_check_healthy(
        self,
        mock_health_check,
        client: TestClient
    ):
        """测试健康检查 - 健康状态"""
        mock_health_check.return_value = True
        
        response = client.get("/api/v1/ai/health?provider=doubao")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "providers" in data
        assert "timestamp" in data
        assert data["providers"]["doubao"]["status"] == "healthy"
        assert data["providers"]["doubao"]["available"] is True
    
    @patch('app.core.config.settings.doubao_api_key', 'test-key')
    @patch('app.services.ai.doubao.DoubaoProvider.health_check')
    def test_health_check_unhealthy(
        self,
        mock_health_check,
        client: TestClient
    ):
        """测试健康检查 - 不健康状态"""
        mock_health_check.return_value = False
        
        response = client.get("/api/v1/ai/health?provider=doubao")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["providers"]["doubao"]["status"] == "unhealthy"
        assert data["providers"]["doubao"]["available"] is True
    
    def test_health_check_no_api_key(self, client: TestClient):
        """测试健康检查 - 没有API密钥"""
        response = client.get("/api/v1/ai/health?provider=doubao")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["providers"]["doubao"]["status"] == "unavailable"
        assert data["providers"]["doubao"]["available"] is False
        assert "API key not configured" in data["providers"]["doubao"]["error"]
    
    def test_health_check_all_providers(self, client: TestClient):
        """测试所有提供商的健康检查"""
        response = client.get("/api/v1/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "providers" in data
        assert "doubao" in data["providers"]
        assert "deepseek" in data["providers"]
        
        # 由于没有API密钥，所有提供商都应该是不可用状态
        for provider_name, provider_data in data["providers"].items():
            assert provider_data["available"] is False
            assert provider_data["status"] == "unavailable"
