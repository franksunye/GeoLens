"""
API客户端
统一的HTTP客户端，处理与后端API的通信
"""

import httpx
import streamlit as st
from typing import Dict, Any, Optional, Union
import json
from datetime import datetime

from utils.config import get_config
from utils.session import get_auth_headers, is_token_expired
from components.auth import AuthManager

class APIClient:
    """API客户端类"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.api_base_url
        self.timeout = self.config.api_timeout
        self.max_retries = self.config.max_retries
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """发送HTTP请求"""
        
        # 构建完整URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # 准备请求头
        request_headers = {"Content-Type": "application/json"}
        
        # 添加认证头
        if require_auth:
            auth_headers = get_auth_headers()
            if not auth_headers and not self._is_demo_mode():
                raise Exception("未认证，请先登录")
            request_headers.update(auth_headers)
        
        # 添加自定义头
        if headers:
            request_headers.update(headers)
        
        # 发送请求
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers
                )
                
                return self._handle_response(response)
                
            except httpx.TimeoutException:
                raise Exception("请求超时，请检查网络连接")
            except httpx.ConnectError:
                raise Exception("无法连接到服务器")
            except Exception as e:
                raise Exception(f"请求失败: {str(e)}")
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """处理响应"""
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"detail": response.text}
        
        if response.status_code == 200:
            return response_data
        elif response.status_code == 401:
            # 认证失败，清除认证数据
            from utils.session import clear_auth_data
            clear_auth_data()
            raise Exception("认证失败，请重新登录")
        elif response.status_code == 403:
            raise Exception("权限不足")
        elif response.status_code == 404:
            raise Exception("资源不存在")
        elif response.status_code == 422:
            # 验证错误
            detail = response_data.get("detail", "数据验证失败")
            if isinstance(detail, list) and detail:
                error_msg = detail[0].get("msg", "数据验证失败")
            else:
                error_msg = str(detail)
            raise Exception(f"数据验证失败: {error_msg}")
        else:
            error_msg = response_data.get("detail", f"请求失败 (状态码: {response.status_code})")
            raise Exception(error_msg)
    
    def _is_demo_mode(self) -> bool:
        """检查是否为演示模式"""
        return st.session_state.get('access_token') == 'demo-access-token'
    
    # 便捷方法
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return await self.request("GET", endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return await self.request("POST", endpoint, data=data, **kwargs)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """PUT请求"""
        return await self.request("PUT", endpoint, data=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE请求"""
        return await self.request("DELETE", endpoint, **kwargs)

class SyncAPIClient:
    """同步API客户端（用于Streamlit）"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.api_base_url
        self.timeout = self.config.api_timeout
    
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """发送同步HTTP请求"""
        
        # 演示模式处理
        if self._is_demo_mode():
            return self._handle_demo_request(method, endpoint, data, params)
        
        # 构建完整URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # 准备请求头
        request_headers = {"Content-Type": "application/json"}
        
        # 添加认证头
        if require_auth:
            auth_headers = get_auth_headers()
            if not auth_headers:
                raise Exception("未认证，请先登录")
            request_headers.update(auth_headers)
        
        # 添加自定义头
        if headers:
            request_headers.update(headers)
        
        # 发送请求
        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers
                )
                
                return self._handle_response(response)
                
            except httpx.TimeoutException:
                raise Exception("请求超时，请检查网络连接")
            except httpx.ConnectError:
                raise Exception("无法连接到服务器")
            except Exception as e:
                raise Exception(f"请求失败: {str(e)}")
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """处理响应"""
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"detail": response.text}
        
        if response.status_code == 200:
            return response_data
        elif response.status_code == 401:
            # 认证失败
            raise Exception("认证失败，请重新登录")
        elif response.status_code == 403:
            raise Exception("权限不足")
        elif response.status_code == 404:
            raise Exception("资源不存在")
        else:
            error_msg = response_data.get("detail", f"请求失败 (状态码: {response.status_code})")
            raise Exception(error_msg)
    
    def _is_demo_mode(self) -> bool:
        """检查是否为演示模式"""
        return st.session_state.get('access_token') == 'demo-access-token'
    
    def _handle_demo_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]], params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """处理演示模式请求"""
        
        # 模拟API响应
        if endpoint.startswith("projects"):
            return self._mock_projects_response(method, endpoint, data)
        elif endpoint.startswith("api/check-mention"):
            return self._mock_detection_response(data)
        elif endpoint.startswith("api/get-history"):
            return self._mock_history_response()
        elif endpoint.startswith("api/templates"):
            return self._mock_templates_response(method, data)
        else:
            return {"data": {}, "message": "演示模式响应"}
    
    def _mock_projects_response(self, method: str, endpoint: str, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """模拟项目API响应"""
        if method == "GET":
            return {
                "data": {
                    "items": [
                        {
                            "id": "demo-project-1",
                            "name": "SaaS工具监测",
                            "domain": "saas-tools.com",
                            "description": "监测SaaS工具在AI中的提及情况",
                            "brands": ["Notion", "Obsidian", "Roam Research"],
                            "created_at": "2024-12-19T10:00:00Z",
                            "is_active": True
                        },
                        {
                            "id": "demo-project-2", 
                            "name": "设计工具分析",
                            "domain": "design-tools.com",
                            "description": "分析设计工具的AI可见性",
                            "brands": ["Figma", "Sketch", "Adobe XD"],
                            "created_at": "2024-12-18T15:30:00Z",
                            "is_active": True
                        }
                    ],
                    "total": 2,
                    "page": 1,
                    "size": 20
                },
                "message": "项目列表获取成功"
            }
        elif method == "POST":
            return {
                "data": {
                    "id": f"demo-project-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "name": data.get("name", "新项目"),
                    "domain": data.get("domain", ""),
                    "description": data.get("description", ""),
                    "brands": data.get("brands", []),
                    "created_at": datetime.now().isoformat(),
                    "is_active": True
                },
                "message": "项目创建成功"
            }
        else:
            return {"data": {}, "message": "操作成功"}
    
    def _mock_detection_response(self, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """模拟检测API响应"""
        import random
        
        brands = data.get("brands", [])
        models = data.get("models", [])
        
        # 生成模拟结果
        brand_mentions = []
        for brand in brands:
            for model in models:
                if random.choice([True, False]):  # 50%概率被提及
                    brand_mentions.append({
                        "brand": brand,
                        "model": model,
                        "mentioned": True,
                        "confidence_score": round(random.uniform(0.7, 0.95), 2),
                        "context_snippet": f"推荐使用{brand}，它是一个优秀的工具...",
                        "position": random.randint(50, 200)
                    })
        
        return {
            "data": {
                "check_id": f"check_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "completed",
                "total_mentions": len(brand_mentions),
                "mention_rate": round(len(brand_mentions) / (len(brands) * len(models)) * 100, 1),
                "brand_mentions": brand_mentions,
                "created_at": datetime.now().isoformat()
            },
            "message": "检测完成"
        }
    
    def _mock_history_response(self) -> Dict[str, Any]:
        """模拟历史记录响应"""
        return {
            "data": {
                "items": [
                    {
                        "id": "history-1",
                        "prompt": "推荐几个好用的笔记软件",
                        "brands_checked": ["Notion", "Obsidian"],
                        "models_used": ["doubao", "deepseek"],
                        "total_mentions": 3,
                        "mention_rate": 75.0,
                        "created_at": "2024-12-19T14:30:00Z",
                        "status": "completed"
                    }
                ],
                "total": 1
            },
            "message": "历史记录获取成功"
        }
    
    def _mock_templates_response(self, method: str, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """模拟模板API响应"""
        if method == "GET":
            return {
                "data": [
                    {
                        "id": "template-1",
                        "name": "笔记软件推荐",
                        "template": "推荐几个好用的{category}软件",
                        "variables": ["category"],
                        "category": "productivity",
                        "usage_count": 15
                    }
                ],
                "message": "模板列表获取成功"
            }
        else:
            return {"data": {}, "message": "操作成功"}
    
    # 便捷方法
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return self.request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return self.request("POST", endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """PUT请求"""
        return self.request("PUT", endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE请求"""
        return self.request("DELETE", endpoint, **kwargs)
