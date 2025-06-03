"""
AI服务单元测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List

from app.services.ai import (
    AIProvider, AIMessage, AIResponse, AIError, AIRole,
    AIServiceFactory, DoubaoProvider, DeepSeekProvider
)


class TestAIServiceFactory:
    """AI服务工厂测试"""
    
    def test_list_providers(self):
        """测试获取提供商列表"""
        providers = AIServiceFactory.list_providers()
        assert "doubao" in providers
        assert "deepseek" in providers
    
    def test_create_doubao_provider(self):
        """测试创建豆包提供商"""
        provider = AIServiceFactory.create_provider(
            "doubao",
            api_key="test-key",
            base_url="https://test.com"
        )
        assert isinstance(provider, DoubaoProvider)
        assert provider.api_key == "test-key"
    
    def test_create_deepseek_provider(self):
        """测试创建DeepSeek提供商"""
        provider = AIServiceFactory.create_provider(
            "deepseek",
            api_key="test-key"
        )
        assert isinstance(provider, DeepSeekProvider)
        assert provider.api_key == "test-key"
    
    def test_create_unsupported_provider(self):
        """测试创建不支持的提供商"""
        with pytest.raises(ValueError, match="Unsupported AI provider"):
            AIServiceFactory.create_provider("unsupported", "test-key")
    
    def test_get_provider_singleton(self):
        """测试获取提供商单例"""
        AIServiceFactory.clear_instances()
        
        provider1 = AIServiceFactory.get_provider("doubao", "test-key")
        provider2 = AIServiceFactory.get_provider("doubao")
        
        assert provider1 is provider2
        
        AIServiceFactory.clear_instances()
    
    def test_get_provider_without_key(self):
        """测试没有API密钥时获取提供商"""
        AIServiceFactory.clear_instances()
        
        with pytest.raises(ValueError, match="API key required"):
            AIServiceFactory.get_provider("doubao")


class TestDoubaoProvider:
    """豆包提供商测试"""
    
    def test_provider_properties(self):
        """测试提供商属性"""
        provider = DoubaoProvider("test-key")
        
        assert provider.provider_name == "doubao"
        assert "doubao-pro-32k" in provider.supported_models
        assert provider.default_model == "doubao-pro-32k"
    
    def test_validate_config_missing_key(self):
        """测试配置验证 - 缺少API密钥"""
        with pytest.raises(ValueError, match="API key is required"):
            DoubaoProvider("")
    
    def test_validate_config_invalid_model(self):
        """测试配置验证 - 无效模型"""
        with pytest.raises(ValueError, match="Unsupported model"):
            DoubaoProvider("test-key", default_model="invalid-model")
    
    def test_prepare_messages(self):
        """测试消息格式准备"""
        provider = DoubaoProvider("test-key")
        messages = [
            AIMessage(role=AIRole.SYSTEM, content="System message"),
            AIMessage(role=AIRole.USER, content="User message")
        ]
        
        formatted = provider._prepare_messages(messages)
        
        assert len(formatted) == 2
        assert formatted[0]["role"] == "system"
        assert formatted[0]["content"] == "System message"
        assert formatted[1]["role"] == "user"
        assert formatted[1]["content"] == "User message"
    
    @pytest.mark.asyncio
    async def test_chat_completion_empty_messages(self):
        """测试空消息列表"""
        provider = DoubaoProvider("test-key")
        
        with pytest.raises(AIError, match="Messages cannot be empty"):
            await provider.chat_completion([])
    
    @pytest.mark.asyncio
    async def test_chat_completion_unsupported_model(self):
        """测试不支持的模型"""
        provider = DoubaoProvider("test-key")
        messages = [AIMessage(role=AIRole.USER, content="Test")]
        
        with pytest.raises(AIError, match="Unsupported model"):
            await provider.chat_completion(messages, model="invalid-model")
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_chat_completion_success(self, mock_client):
        """测试成功的聊天完成"""
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "Test response"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            },
            "id": "test-id"
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        provider = DoubaoProvider("test-key")
        messages = [AIMessage(role=AIRole.USER, content="Test message")]
        
        response = await provider.chat_completion(messages)
        
        assert response.content == "Test response"
        assert response.provider == "doubao"
        assert response.usage["total_tokens"] == 15
        assert response.metadata["response_id"] == "test-id"
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_chat_completion_http_error(self, mock_client):
        """测试HTTP错误"""
        import httpx
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = httpx.HTTPStatusError(
            "HTTP Error", request=MagicMock(), response=MagicMock(status_code=400, text="Bad Request")
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        provider = DoubaoProvider("test-key")
        messages = [AIMessage(role=AIRole.USER, content="Test")]
        
        with pytest.raises(AIError, match="HTTP 400"):
            await provider.chat_completion(messages)


class TestDeepSeekProvider:
    """DeepSeek提供商测试"""
    
    def test_provider_properties(self):
        """测试提供商属性"""
        provider = DeepSeekProvider("test-key")
        
        assert provider.provider_name == "deepseek"
        assert "deepseek-chat" in provider.supported_models
        assert provider.default_model == "deepseek-chat"
    
    def test_validate_config_missing_key(self):
        """测试配置验证 - 缺少API密钥"""
        with pytest.raises(ValueError, match="API key is required"):
            DeepSeekProvider("")
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_chat_completion_with_reasoning(self, mock_client):
        """测试带推理过程的聊天完成"""
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Final answer",
                    "reasoning_content": "Reasoning process"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 10,
                "total_tokens": 30
            },
            "id": "deepseek-id",
            "created": 1234567890
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        provider = DeepSeekProvider("test-key")
        messages = [AIMessage(role=AIRole.USER, content="Test message")]
        
        response = await provider.chat_completion(messages)
        
        assert response.content == "Final answer"
        assert response.provider == "deepseek"
        assert response.metadata["reasoning_content"] == "Reasoning process"
        assert response.metadata["created"] == 1234567890


class TestAIMessage:
    """AI消息测试"""
    
    def test_create_message(self):
        """测试创建消息"""
        message = AIMessage(
            role=AIRole.USER,
            content="Test content",
            metadata={"key": "value"}
        )
        
        assert message.role == AIRole.USER
        assert message.content == "Test content"
        assert message.metadata["key"] == "value"


class TestAIResponse:
    """AI响应测试"""
    
    def test_create_response(self):
        """测试创建响应"""
        response = AIResponse(
            content="Response content",
            model="test-model",
            provider="test-provider",
            usage={"total_tokens": 100},
            response_time=1.5,
            metadata={"key": "value"}
        )
        
        assert response.content == "Response content"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.usage["total_tokens"] == 100
        assert response.response_time == 1.5
        assert response.metadata["key"] == "value"


class TestAIError:
    """AI错误测试"""
    
    def test_create_error(self):
        """测试创建错误"""
        error = AIError(
            message="Test error",
            provider="test-provider",
            error_code="TEST_ERROR"
        )
        
        assert str(error) == "Test error"
        assert error.provider == "test-provider"
        assert error.error_code == "TEST_ERROR"
