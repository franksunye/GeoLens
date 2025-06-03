"""
豆包(火山引擎)AI服务提供商

集成火山引擎豆包大模型API。
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, AsyncGenerator

import httpx
from .base import AIProvider, AIMessage, AIResponse, AIError, AIRole


class DoubaoProvider(AIProvider):
    """豆包AI服务提供商"""
    
    def __init__(self, api_key: str, **kwargs):
        self.base_url = kwargs.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
        self.default_model = kwargs.get("default_model", "doubao-pro-32k")
        self.timeout = kwargs.get("timeout", 30)
        super().__init__(api_key, **kwargs)
    
    @property
    def provider_name(self) -> str:
        return "doubao"
    
    @property
    def supported_models(self) -> List[str]:
        return [
            "doubao-pro-32k",
            "doubao-pro-256k", 
            "doubao-lite-32k",
            "doubao-lite-128k",
            "doubao-lite-4k",
            "doubao-vision-pro",
            "doubao-vision-lite",
            "doubao-1.5-pro-32k",
            "doubao-1.5-lite",
        ]
    
    def _validate_config(self) -> None:
        """验证配置参数"""
        if not self.api_key:
            raise ValueError("API key is required for Doubao provider")
        
        if self.default_model not in self.supported_models:
            raise ValueError(f"Unsupported model: {self.default_model}")
    
    def _prepare_messages(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """准备消息格式"""
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        return formatted_messages
    
    def _prepare_headers(self) -> Dict[str, str]:
        """准备请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def chat_completion(
        self,
        messages: List[AIMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> AIResponse:
        """聊天完成接口"""
        start_time = time.time()
        
        if not messages:
            raise AIError("Messages cannot be empty", self.provider_name)
        
        model = model or self.default_model
        if model not in self.supported_models:
            raise AIError(f"Unsupported model: {model}", self.provider_name)
        
        # 准备请求数据
        request_data = {
            "model": model,
            "messages": self._prepare_messages(messages),
            "temperature": max(0.0, min(1.0, temperature)),
            "max_tokens": max(1, min(4096, max_tokens)),
            "stream": stream,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._prepare_headers(),
                    json=request_data
                )
                response.raise_for_status()
                
                result = response.json()
                
                # 解析响应
                if "choices" not in result or not result["choices"]:
                    raise AIError("Invalid response format", self.provider_name)
                
                choice = result["choices"][0]
                content = choice.get("message", {}).get("content", "")
                
                # 使用情况
                usage = result.get("usage", {})
                usage_dict = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
                
                return self._create_response(
                    content=content,
                    model=model,
                    usage=usage_dict,
                    start_time=start_time,
                    metadata={
                        "finish_reason": choice.get("finish_reason"),
                        "response_id": result.get("id"),
                    }
                )
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise AIError(error_msg, self.provider_name, str(e.response.status_code))
        except httpx.RequestError as e:
            raise AIError(f"Request failed: {str(e)}", self.provider_name)
        except json.JSONDecodeError as e:
            raise AIError(f"Invalid JSON response: {str(e)}", self.provider_name)
        except Exception as e:
            raise AIError(f"Unexpected error: {str(e)}", self.provider_name)
    
    async def chat_completion_stream(
        self,
        messages: List[AIMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成接口"""
        if not messages:
            raise AIError("Messages cannot be empty", self.provider_name)
        
        model = model or self.default_model
        if model not in self.supported_models:
            raise AIError(f"Unsupported model: {model}", self.provider_name)
        
        # 准备请求数据
        request_data = {
            "model": model,
            "messages": self._prepare_messages(messages),
            "temperature": max(0.0, min(1.0, temperature)),
            "max_tokens": max(1, min(4096, max_tokens)),
            "stream": True,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._prepare_headers(),
                    json=request_data
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # 移除 "data: " 前缀
                            
                            if data.strip() == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise AIError(error_msg, self.provider_name, str(e.response.status_code))
        except httpx.RequestError as e:
            raise AIError(f"Request failed: {str(e)}", self.provider_name)
        except Exception as e:
            raise AIError(f"Unexpected error: {str(e)}", self.provider_name)
