"""
检测服务
处理AI引用检测相关的业务逻辑
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from services.api_client import SyncAPIClient
from utils.session import update_cache, get_cache

class DetectionService:
    """检测服务类"""
    
    def __init__(self):
        self.api_client = SyncAPIClient()
    
    def run_detection(
        self,
        project_id: str,
        prompt: str,
        brands: List[str],
        models: List[str],
        max_tokens: int = 300,
        temperature: float = 0.3,
        parallel_execution: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行引用检测"""
        
        try:
            # 准备检测参数
            detection_data = {
                "project_id": project_id,
                "prompt": prompt,
                "brands": brands,
                "models": models,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "parallel_execution": parallel_execution,
                "metadata": metadata or {}
            }
            
            # 调用检测API
            response = self.api_client.post("api/check-mention", data=detection_data)
            
            # 缓存结果
            if response.get("data"):
                cache_key = f"detection_{response['data'].get('check_id')}"
                update_cache(cache_key, response["data"], ttl=3600)  # 缓存1小时
            
            return response
            
        except Exception as e:
            st.error(f"检测失败: {str(e)}")
            raise e
    
    def get_detection_history(
        self,
        project_id: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取检测历史"""
        
        # 检查缓存
        cache_key = f"history_{project_id}_{page}_{size}_{status}"
        cached_data = get_cache(cache_key)
        if cached_data:
            return {"data": cached_data, "message": "从缓存获取"}
        
        try:
            # 准备查询参数
            params = {
                "page": page,
                "size": size
            }
            
            if project_id:
                params["project_id"] = project_id
            
            if status:
                params["status"] = status
            
            # 调用历史API
            response = self.api_client.get("api/get-history", params=params)
            
            # 缓存结果
            if response.get("data"):
                update_cache(cache_key, response["data"], ttl=300)  # 缓存5分钟
            
            return response
            
        except Exception as e:
            st.error(f"获取历史记录失败: {str(e)}")
            raise e
    
    def get_detection_detail(self, check_id: str) -> Dict[str, Any]:
        """获取检测详情"""
        
        # 检查缓存
        cache_key = f"detection_{check_id}"
        cached_data = get_cache(cache_key)
        if cached_data:
            return {"data": cached_data, "message": "从缓存获取"}
        
        try:
            response = self.api_client.get(f"api/get-history/{check_id}")
            
            # 缓存结果
            if response.get("data"):
                update_cache(cache_key, response["data"], ttl=3600)
            
            return response
            
        except Exception as e:
            st.error(f"获取检测详情失败: {str(e)}")
            raise e
    
    def get_brand_analytics(
        self,
        project_id: str,
        brands: List[str],
        timeframe: str = "30d"
    ) -> Dict[str, Any]:
        """获取品牌分析数据"""
        
        # 检查缓存
        cache_key = f"analytics_{project_id}_{'-'.join(brands)}_{timeframe}"
        cached_data = get_cache(cache_key)
        if cached_data:
            return {"data": cached_data, "message": "从缓存获取"}
        
        try:
            params = {
                "project_id": project_id,
                "brands": brands,
                "timeframe": timeframe
            }
            
            response = self.api_client.get("api/get-mention-analytics", params=params)
            
            # 缓存结果
            if response.get("data"):
                update_cache(cache_key, response["data"], ttl=600)  # 缓存10分钟
            
            return response
            
        except Exception as e:
            st.error(f"获取品牌分析失败: {str(e)}")
            raise e
    
    def compare_brands(
        self,
        project_id: str,
        brands: List[str],
        prompt: str,
        models: List[str]
    ) -> Dict[str, Any]:
        """品牌对比分析"""
        
        try:
            comparison_data = {
                "project_id": project_id,
                "brands": brands,
                "prompt": prompt,
                "models": models
            }
            
            response = self.api_client.post("api/compare", data=comparison_data)
            
            return response
            
        except Exception as e:
            st.error(f"品牌对比失败: {str(e)}")
            raise e
    
    def export_detection_results(
        self,
        check_ids: List[str],
        format: str = "csv"
    ) -> Dict[str, Any]:
        """导出检测结果"""
        
        try:
            export_data = {
                "check_ids": check_ids,
                "format": format
            }
            
            response = self.api_client.post("api/export", data=export_data)
            
            return response
            
        except Exception as e:
            st.error(f"导出失败: {str(e)}")
            raise e
    
    def delete_detection_record(self, check_id: str) -> bool:
        """删除检测记录"""
        
        try:
            response = self.api_client.delete(f"api/get-history/{check_id}")
            
            # 清除相关缓存
            cache_key = f"detection_{check_id}"
            if cache_key in st.session_state.get('history_cache', {}):
                del st.session_state.history_cache[cache_key]
            
            return True
            
        except Exception as e:
            st.error(f"删除记录失败: {str(e)}")
            return False

class TemplateService:
    """模板服务类"""
    
    def __init__(self):
        self.api_client = SyncAPIClient()
    
    def get_templates(
        self,
        category: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取模板列表"""
        
        # 检查缓存
        cache_key = f"templates_{category}_{user_id}"
        cached_data = get_cache(cache_key)
        if cached_data:
            return {"data": cached_data, "message": "从缓存获取"}
        
        try:
            params = {}
            if category:
                params["category"] = category
            if user_id:
                params["user_id"] = user_id
            
            response = self.api_client.get("api/templates", params=params)
            
            # 缓存结果
            if response.get("data"):
                update_cache(cache_key, response["data"], ttl=600)  # 缓存10分钟
            
            return response
            
        except Exception as e:
            st.error(f"获取模板失败: {str(e)}")
            raise e
    
    def create_template(
        self,
        name: str,
        template: str,
        category: str,
        description: Optional[str] = None,
        variables: Optional[List[str]] = None,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """创建模板"""
        
        try:
            template_data = {
                "name": name,
                "template": template,
                "category": category,
                "description": description,
                "variables": variables or [],
                "is_public": is_public
            }
            
            response = self.api_client.post("api/templates", data=template_data)
            
            # 清除模板缓存
            from utils.session import clear_cache
            clear_cache("templates")
            
            return response
            
        except Exception as e:
            st.error(f"创建模板失败: {str(e)}")
            raise e
    
    def update_template(
        self,
        template_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """更新模板"""
        
        try:
            response = self.api_client.put(f"api/templates/{template_id}", data=kwargs)
            
            # 清除模板缓存
            from utils.session import clear_cache
            clear_cache("templates")
            
            return response
            
        except Exception as e:
            st.error(f"更新模板失败: {str(e)}")
            raise e
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        
        try:
            response = self.api_client.delete(f"api/templates/{template_id}")
            
            # 清除模板缓存
            from utils.session import clear_cache
            clear_cache("templates")
            
            return True
            
        except Exception as e:
            st.error(f"删除模板失败: {str(e)}")
            return False
    
    def apply_template(
        self,
        template_id: str,
        variables: Dict[str, str]
    ) -> str:
        """应用模板"""
        
        try:
            # 获取模板详情
            response = self.api_client.get(f"api/templates/{template_id}")
            template_data = response.get("data", {})
            
            # 替换变量
            template_text = template_data.get("template", "")
            for var_name, var_value in variables.items():
                template_text = template_text.replace(f"{{{var_name}}}", var_value)
            
            return template_text
            
        except Exception as e:
            st.error(f"应用模板失败: {str(e)}")
            return ""
    
    def extract_variables(self, template_text: str) -> List[str]:
        """提取模板变量"""
        import re
        
        # 使用正则表达式提取 {variable} 格式的变量
        variables = re.findall(r'\{(\w+)\}', template_text)
        return list(set(variables))  # 去重
