"""
认证管理组件
处理用户登录、注册和认证状态管理
"""

import streamlit as st
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from utils.config import get_config
from utils.session import set_auth_data, clear_auth_data, is_token_expired, get_auth_headers

class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.config = get_config()
        self.api_base_url = self.config.api_base_url
    
    def login(self, email: str, password: str) -> bool:
        """用户登录"""
        try:
            # 演示模式 - 直接成功
            if email == "demo@geolens.ai" and password == "demo123":
                # 模拟用户数据
                user_data = {
                    "id": "demo-user-id",
                    "email": "demo@geolens.ai",
                    "full_name": "演示用户",
                    "is_active": True,
                    "subscription_plan": "free"
                }
                
                # 模拟token
                access_token = "demo-access-token"
                refresh_token = "demo-refresh-token"
                
                # 设置认证数据
                set_auth_data(access_token, refresh_token, user_data, expires_in=3600)
                
                return True
            
            # 真实API调用
            login_url = self.config.get_api_url("auth/login")
            
            with httpx.Client(timeout=self.config.api_timeout) as client:
                response = client.post(
                    login_url,
                    json={"email": email, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()["data"]
                    
                    # 设置认证数据
                    set_auth_data(
                        access_token=data["access_token"],
                        refresh_token=data["refresh_token"],
                        user_data=data["user"],
                        expires_in=data.get("expires_in", 3600)
                    )
                    
                    return True
                else:
                    st.error(f"登录失败: {response.json().get('detail', '未知错误')}")
                    return False
                    
        except httpx.TimeoutException:
            st.error("❌ 请求超时，请检查网络连接")
            return False
        except httpx.ConnectError:
            st.error("❌ 无法连接到服务器，请检查API地址配置")
            return False
        except Exception as e:
            st.error(f"❌ 登录过程中发生错误: {str(e)}")
            return False
    
    def logout(self):
        """用户登出"""
        clear_auth_data()
        st.success("✅ 已成功登出")
        st.rerun()
    
    def register(self, email: str, password: str, full_name: str) -> bool:
        """用户注册"""
        try:
            register_url = self.config.get_api_url("auth/register")
            
            with httpx.Client(timeout=self.config.api_timeout) as client:
                response = client.post(
                    register_url,
                    json={
                        "email": email,
                        "password": password,
                        "full_name": full_name
                    }
                )
                
                if response.status_code == 200:
                    st.success("✅ 注册成功！请使用新账号登录")
                    return True
                else:
                    error_msg = response.json().get('detail', '注册失败')
                    st.error(f"❌ {error_msg}")
                    return False
                    
        except Exception as e:
            st.error(f"❌ 注册过程中发生错误: {str(e)}")
            return False
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        if not st.session_state.authenticated:
            return False
        
        if not st.session_state.access_token:
            return False
        
        # 检查token是否过期
        if is_token_expired():
            # 尝试刷新token
            if not self.refresh_token():
                clear_auth_data()
                return False
        
        return True
    
    def refresh_token(self) -> bool:
        """刷新访问令牌"""
        if not st.session_state.refresh_token:
            return False
        
        try:
            # 演示模式 - 直接成功
            if st.session_state.refresh_token == "demo-refresh-token":
                # 更新token过期时间
                st.session_state.token_expires_at = datetime.now() + timedelta(hours=1)
                return True
            
            # 真实API调用
            refresh_url = self.config.get_api_url("auth/refresh")
            
            with httpx.Client(timeout=self.config.api_timeout) as client:
                response = client.post(
                    refresh_url,
                    json={"refresh_token": st.session_state.refresh_token}
                )
                
                if response.status_code == 200:
                    data = response.json()["data"]
                    
                    # 更新访问令牌
                    st.session_state.access_token = data["access_token"]
                    st.session_state.token_expires_at = datetime.now() + timedelta(
                        seconds=data.get("expires_in", 3600)
                    )
                    
                    return True
                else:
                    return False
                    
        except Exception:
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        if not self.is_authenticated():
            return None
        
        return st.session_state.user
    
    def update_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        """更新用户资料"""
        if not self.is_authenticated():
            return False
        
        try:
            update_url = self.config.get_api_url("auth/me")
            headers = get_auth_headers()
            
            with httpx.Client(timeout=self.config.api_timeout) as client:
                response = client.put(
                    update_url,
                    json=profile_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    # 更新会话中的用户数据
                    updated_user = response.json()["data"]
                    st.session_state.user.update(updated_user)
                    
                    st.success("✅ 用户资料更新成功")
                    return True
                else:
                    error_msg = response.json().get('detail', '更新失败')
                    st.error(f"❌ {error_msg}")
                    return False
                    
        except Exception as e:
            st.error(f"❌ 更新过程中发生错误: {str(e)}")
            return False

def show_login_form():
    """显示登录表单"""
    st.markdown("### 🔐 用户登录")
    
    with st.form("login_form"):
        email = st.text_input("📧 邮箱地址", placeholder="请输入您的邮箱")
        password = st.text_input("🔒 密码", type="password", placeholder="请输入密码")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("🚀 登录", type="primary")
        with col2:
            register_button = st.form_submit_button("📝 注册")
    
    if login_button:
        if email and password:
            auth_manager = AuthManager()
            if auth_manager.login(email, password):
                st.success("✅ 登录成功！")
                st.rerun()
        else:
            st.warning("⚠️ 请填写完整的登录信息")
    
    if register_button:
        st.info("📝 注册功能开发中，请联系管理员获取账号")

def show_register_form():
    """显示注册表单"""
    st.markdown("### 📝 用户注册")
    
    with st.form("register_form"):
        email = st.text_input("📧 邮箱地址", placeholder="请输入您的邮箱")
        full_name = st.text_input("👤 姓名", placeholder="请输入您的姓名")
        password = st.text_input("🔒 密码", type="password", placeholder="请输入密码")
        confirm_password = st.text_input("🔒 确认密码", type="password", placeholder="请再次输入密码")
        
        register_button = st.form_submit_button("📝 注册", type="primary")
    
    if register_button:
        if not all([email, full_name, password, confirm_password]):
            st.warning("⚠️ 请填写完整的注册信息")
        elif password != confirm_password:
            st.error("❌ 两次输入的密码不一致")
        elif len(password) < 6:
            st.error("❌ 密码长度至少6位")
        else:
            auth_manager = AuthManager()
            if auth_manager.register(email, password, full_name):
                st.success("✅ 注册成功！请使用新账号登录")

def require_auth(func):
    """认证装饰器"""
    def wrapper(*args, **kwargs):
        auth_manager = AuthManager()
        if not auth_manager.is_authenticated():
            st.error("❌ 请先登录")
            st.stop()
        return func(*args, **kwargs)
    return wrapper
