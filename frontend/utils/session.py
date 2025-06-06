"""
会话状态管理模块
管理Streamlit会话状态和用户数据
"""

import streamlit as st
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

def init_session_state():
    """初始化会话状态"""
    
    # 认证相关
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    
    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = None
    
    if 'token_expires_at' not in st.session_state:
        st.session_state.token_expires_at = None
    
    if 'user' not in st.session_state:
        st.session_state.user = {}
    
    # 应用状态
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None
    
    if 'selected_brands' not in st.session_state:
        st.session_state.selected_brands = []
    
    if 'selected_models' not in st.session_state:
        st.session_state.selected_models = ["doubao", "deepseek"]
    
    # 缓存数据
    if 'projects_cache' not in st.session_state:
        st.session_state.projects_cache = {}
    
    if 'templates_cache' not in st.session_state:
        st.session_state.templates_cache = {}
    
    if 'history_cache' not in st.session_state:
        st.session_state.history_cache = {}
    
    # UI状态
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = "expanded"
    
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"
    
    # 检测状态
    if 'detection_running' not in st.session_state:
        st.session_state.detection_running = False
    
    if 'last_detection_result' not in st.session_state:
        st.session_state.last_detection_result = None

def set_auth_data(access_token: str, refresh_token: str, user_data: Dict[str, Any], expires_in: int = 3600):
    """设置认证数据"""
    st.session_state.authenticated = True
    st.session_state.access_token = access_token
    st.session_state.refresh_token = refresh_token
    st.session_state.user = user_data
    st.session_state.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

def clear_auth_data():
    """清除认证数据"""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = {}
    st.session_state.token_expires_at = None
    
    # 清除缓存数据
    st.session_state.projects_cache = {}
    st.session_state.templates_cache = {}
    st.session_state.history_cache = {}

def is_token_expired() -> bool:
    """检查token是否过期"""
    if not st.session_state.token_expires_at:
        return True
    
    return datetime.now() >= st.session_state.token_expires_at

def get_auth_headers() -> Dict[str, str]:
    """获取认证头"""
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

def set_current_project(project_data: Dict[str, Any]):
    """设置当前项目"""
    st.session_state.current_project = project_data

def get_current_project() -> Optional[Dict[str, Any]]:
    """获取当前项目"""
    return st.session_state.current_project

def update_cache(cache_key: str, data: Any, ttl: int = 300):
    """更新缓存数据"""
    cache_data = {
        'data': data,
        'expires_at': datetime.now() + timedelta(seconds=ttl)
    }
    
    if cache_key.startswith('projects'):
        st.session_state.projects_cache[cache_key] = cache_data
    elif cache_key.startswith('templates'):
        st.session_state.templates_cache[cache_key] = cache_data
    elif cache_key.startswith('history'):
        st.session_state.history_cache[cache_key] = cache_data

def get_cache(cache_key: str) -> Optional[Any]:
    """获取缓存数据"""
    cache_dict = None
    
    if cache_key.startswith('projects'):
        cache_dict = st.session_state.projects_cache
    elif cache_key.startswith('templates'):
        cache_dict = st.session_state.templates_cache
    elif cache_key.startswith('history'):
        cache_dict = st.session_state.history_cache
    
    if cache_dict and cache_key in cache_dict:
        cache_data = cache_dict[cache_key]
        
        # 检查是否过期
        if datetime.now() < cache_data['expires_at']:
            return cache_data['data']
        else:
            # 删除过期缓存
            del cache_dict[cache_key]
    
    return None

def clear_cache(cache_type: str = "all"):
    """清除缓存"""
    if cache_type == "all" or cache_type == "projects":
        st.session_state.projects_cache = {}
    
    if cache_type == "all" or cache_type == "templates":
        st.session_state.templates_cache = {}
    
    if cache_type == "all" or cache_type == "history":
        st.session_state.history_cache = {}

def set_detection_state(running: bool, result: Optional[Dict[str, Any]] = None):
    """设置检测状态"""
    st.session_state.detection_running = running
    if result is not None:
        st.session_state.last_detection_result = result

def get_detection_state() -> tuple[bool, Optional[Dict[str, Any]]]:
    """获取检测状态"""
    return st.session_state.detection_running, st.session_state.last_detection_result

def show_session_debug():
    """显示会话调试信息"""
    with st.expander("🔍 会话状态调试", expanded=False):
        st.markdown("### 认证状态")
        st.json({
            "authenticated": st.session_state.authenticated,
            "user_email": st.session_state.user.get('email', '未登录'),
            "token_expires_at": str(st.session_state.token_expires_at) if st.session_state.token_expires_at else None,
            "token_expired": is_token_expired()
        })
        
        st.markdown("### 应用状态")
        st.json({
            "current_project": st.session_state.current_project.get('name', '未选择') if st.session_state.current_project else '未选择',
            "selected_brands": st.session_state.selected_brands,
            "selected_models": st.session_state.selected_models,
            "detection_running": st.session_state.detection_running
        })
        
        st.markdown("### 缓存状态")
        st.json({
            "projects_cache_count": len(st.session_state.projects_cache),
            "templates_cache_count": len(st.session_state.templates_cache),
            "history_cache_count": len(st.session_state.history_cache)
        })
