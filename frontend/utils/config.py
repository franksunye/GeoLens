"""
配置管理模块
管理应用配置和环境变量
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
        self.app_name = "GeoLens"
        self.app_version = "v0.8.0-streamlit-mvp"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # API配置
        self.api_timeout = int(os.getenv("API_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        
        # 缓存配置
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))  # 5分钟
        
        # UI配置
        self.page_size = int(os.getenv("PAGE_SIZE", "20"))
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "10"))  # MB
        
        # AI模型配置
        self.available_models = [
            "doubao",
            "deepseek", 
            "openai"
        ]
        
        # 默认检测配置
        self.default_detection_config = {
            "max_tokens": 300,
            "temperature": 0.3,
            "parallel_execution": True
        }

    def get_api_url(self, endpoint: str) -> str:
        """获取完整的API URL"""
        return f"{self.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "api_base_url": self.api_base_url,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "debug": self.debug,
            "api_timeout": self.api_timeout,
            "max_retries": self.max_retries,
            "cache_ttl": self.cache_ttl,
            "page_size": self.page_size,
            "max_file_size": self.max_file_size,
            "available_models": self.available_models,
            "default_detection_config": self.default_detection_config
        }

# 全局配置实例
_config = None

def load_config() -> Config:
    """加载配置"""
    global _config
    if _config is None:
        _config = Config()
    return _config

def get_config() -> Config:
    """获取配置实例"""
    return load_config()

@st.cache_data(ttl=3600)  # 缓存1小时
def get_cached_config() -> Dict[str, Any]:
    """获取缓存的配置"""
    return get_config().to_dict()

def update_config(**kwargs) -> None:
    """更新配置"""
    global _config
    if _config is None:
        _config = Config()
    
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)

def validate_config() -> bool:
    """验证配置"""
    config = get_config()
    
    # 检查必要的配置项
    required_configs = [
        "api_base_url",
        "app_name",
        "app_version"
    ]
    
    for config_key in required_configs:
        if not getattr(config, config_key, None):
            st.error(f"❌ 缺少必要配置: {config_key}")
            return False
    
    return True

def show_config_debug():
    """显示配置调试信息"""
    if get_config().debug:
        config = get_cached_config()
        
        with st.expander("🔧 配置调试信息", expanded=False):
            st.json(config)
            
            st.markdown("### 环境变量")
            env_vars = {
                "API_BASE_URL": os.getenv("API_BASE_URL", "未设置"),
                "DEBUG": os.getenv("DEBUG", "未设置"),
                "API_TIMEOUT": os.getenv("API_TIMEOUT", "未设置"),
                "CACHE_TTL": os.getenv("CACHE_TTL", "未设置"),
            }
            st.json(env_vars)
