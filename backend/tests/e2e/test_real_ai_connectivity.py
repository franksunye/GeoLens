"""
真实AI模型连通性测试
"""

import pytest
import asyncio
from typing import List

from app.services.ai import AIServiceFactory, AIMessage, AIRole, AIError


@pytest.mark.e2e
class TestRealAIConnectivity:
    """测试真实AI模型的连通性"""

    async def test_doubao_connection(self, skip_if_no_api_keys, ai_factory, e2e_config):
        """测试豆包API连接"""
        try:
            # 获取豆包服务提供商
            doubao_provider = ai_factory.get_provider("doubao")
            
            # 简单的连通性测试
            test_message = [
                AIMessage(role=AIRole.USER, content="你好，请回复'连接成功'")
            ]
            
            response = await doubao_provider.chat_completion(
                messages=test_message,
                model=e2e_config["doubao_model"],
                max_tokens=50,
                temperature=0.1
            )
            
            # 验证响应
            assert response is not None
            assert response.content is not None
            assert len(response.content) > 0
            assert response.provider == "doubao"
            
            print(f"✅ 豆包连接成功: {response.content[:100]}...")
            
        except Exception as e:
            pytest.fail(f"豆包API连接失败: {str(e)}")

    async def test_deepseek_connection(self, skip_if_no_api_keys, ai_factory, e2e_config):
        """测试DeepSeek API连接"""
        try:
            # 获取DeepSeek服务提供商
            deepseek_provider = ai_factory.get_provider("deepseek")
            
            # 简单的连通性测试
            test_message = [
                AIMessage(role=AIRole.USER, content="Hello, please reply 'Connection successful'")
            ]
            
            response = await deepseek_provider.chat_completion(
                messages=test_message,
                model=e2e_config["deepseek_model"],
                max_tokens=50,
                temperature=0.1
            )
            
            # 验证响应
            assert response is not None
            assert response.content is not None
            assert len(response.content) > 0
            assert response.provider == "deepseek"
            
            print(f"✅ DeepSeek连接成功: {response.content[:100]}...")
            
        except Exception as e:
            pytest.fail(f"DeepSeek API连接失败: {str(e)}")

    async def test_api_response_format(self, skip_if_no_api_keys, ai_factory, e2e_config):
        """测试API响应格式的一致性"""
        providers = ["doubao", "deepseek"]
        models = {
            "doubao": e2e_config["doubao_model"],
            "deepseek": e2e_config["deepseek_model"]
        }
        
        test_message = [
            AIMessage(role=AIRole.USER, content="请简单介绍一下人工智能")
        ]
        
        for provider_name in providers:
            try:
                provider = ai_factory.get_provider(provider_name)
                
                response = await provider.chat_completion(
                    messages=test_message,
                    model=models[provider_name],
                    max_tokens=100,
                    temperature=0.5
                )
                
                # 验证响应格式的一致性
                assert hasattr(response, 'content'), f"{provider_name} 响应缺少content字段"
                assert hasattr(response, 'provider'), f"{provider_name} 响应缺少provider字段"
                assert hasattr(response, 'model'), f"{provider_name} 响应缺少model字段"
                assert hasattr(response, 'usage'), f"{provider_name} 响应缺少usage字段"
                
                assert response.provider == provider_name
                assert isinstance(response.content, str)
                assert len(response.content) > 0
                
                print(f"✅ {provider_name} 响应格式验证通过")
                
            except Exception as e:
                pytest.fail(f"{provider_name} 响应格式验证失败: {str(e)}")

    async def test_error_handling(self, skip_if_no_api_keys, ai_factory):
        """测试错误处理机制"""
        providers = ["doubao", "deepseek"]
        
        for provider_name in providers:
            try:
                provider = ai_factory.get_provider(provider_name)
                
                # 测试空消息处理
                with pytest.raises(AIError):
                    await provider.chat_completion(
                        messages=[],  # 空消息列表
                        max_tokens=50
                    )
                
                # 测试无效模型处理
                with pytest.raises(AIError):
                    await provider.chat_completion(
                        messages=[AIMessage(role=AIRole.USER, content="test")],
                        model="invalid-model-name",
                        max_tokens=50
                    )
                
                print(f"✅ {provider_name} 错误处理验证通过")
                
            except Exception as e:
                if not isinstance(e, AIError):
                    pytest.fail(f"{provider_name} 错误处理验证失败: {str(e)}")

    async def test_concurrent_api_calls(self, skip_if_no_api_keys, ai_factory, e2e_config):
        """测试并发API调用"""
        async def call_api(provider_name: str, model: str, content: str):
            """单个API调用"""
            provider = ai_factory.get_provider(provider_name)
            message = [AIMessage(role=AIRole.USER, content=content)]
            
            response = await provider.chat_completion(
                messages=message,
                model=model,
                max_tokens=50,
                temperature=0.1
            )
            
            return {
                "provider": provider_name,
                "content": response.content,
                "success": True
            }
        
        # 准备并发任务
        tasks = [
            call_api("doubao", e2e_config["doubao_model"], "请说'豆包测试1'"),
            call_api("doubao", e2e_config["doubao_model"], "请说'豆包测试2'"),
            call_api("deepseek", e2e_config["deepseek_model"], "Please say 'DeepSeek test 1'"),
            call_api("deepseek", e2e_config["deepseek_model"], "Please say 'DeepSeek test 2'"),
        ]
        
        # 执行并发调用
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证结果
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ 任务 {i+1} 失败: {str(result)}")
            else:
                assert result["success"] is True
                assert len(result["content"]) > 0
                success_count += 1
                print(f"✅ 任务 {i+1} 成功: {result['provider']} - {result['content'][:50]}...")
        
        # 至少要有一半的请求成功
        assert success_count >= len(tasks) // 2, f"并发测试失败，成功率过低: {success_count}/{len(tasks)}"
        
        print(f"✅ 并发测试完成，成功率: {success_count}/{len(tasks)}")
