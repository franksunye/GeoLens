"""
用户资料页面
用户信息管理和设置
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List

from components.auth import require_auth, AuthManager
from components.sidebar import render_sidebar
from utils.config import get_config
from styles.enterprise_theme import apply_enterprise_theme, render_enterprise_header, render_status_badge

# 页面配置
st.set_page_config(
    page_title="个人资料 - GeoLens",
    page_icon="👤",
    layout="wide"
)

# 应用企业级主题
apply_enterprise_theme()

@require_auth
def main():
    """主函数"""
    render_sidebar()
    
    render_enterprise_header("个人资料", "")
    st.markdown("管理您的账户信息和应用设置")
    
    # 主要功能选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["基本信息", "应用设置", "使用统计", "安全设置"])
    
    with tab1:
        render_profile_info()
    
    with tab2:
        render_app_settings()
    
    with tab3:
        render_usage_stats()
    
    with tab4:
        render_security_settings()

def render_profile_info():
    """渲染个人信息"""
    st.markdown("### 基本信息")
    
    # 获取当前用户信息
    auth_manager = AuthManager()
    user = auth_manager.get_current_user()
    
    if not user:
        st.error("无法获取用户信息")
        return
    
    # 用户头像和基本信息
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # 用户头像
        initial = user.get('full_name', user.get('email', 'U'))[0].upper()
        st.markdown(f"""
        <div style="
            width: 120px; 
            height: 120px; 
            border-radius: 50%; 
            background: linear-gradient(45deg, #1f77b4, #ff7f0e);
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: white; 
            font-weight: bold; 
            font-size: 48px;
            margin: 20px auto;
        ">{initial}</div>
        """, unsafe_allow_html=True)
        
        # 上传头像按钮
        uploaded_file = st.file_uploader(
            "更换头像",
            type=['png', 'jpg', 'jpeg'],
            help="支持PNG、JPG格式，文件大小不超过5MB"
        )
        
        if uploaded_file:
            st.info("头像上传功能开发中...")
    
    with col2:
        # 编辑个人信息表单
        with st.form("profile_form"):
            st.markdown("#### 编辑信息")
            
            # 基本信息
            full_name = st.text_input(
                "姓名",
                value=user.get('full_name', ''),
                placeholder="请输入您的姓名"
            )
            
            email = st.text_input(
                "邮箱地址",
                value=user.get('email', ''),
                disabled=True,
                help="邮箱地址不可修改"
            )
            
            # 可选信息
            col_a, col_b = st.columns(2)
            
            with col_a:
                company = st.text_input(
                    "公司/组织",
                    value=user.get('company', ''),
                    placeholder="请输入公司或组织名称"
                )
            
            with col_b:
                job_title = st.text_input(
                    "职位",
                    value=user.get('job_title', ''),
                    placeholder="请输入您的职位"
                )
            
            # 联系信息
            phone = st.text_input(
                "手机号码",
                value=user.get('phone', ''),
                placeholder="请输入手机号码"
            )
            
            # 个人简介
            bio = st.text_area(
                "个人简介",
                value=user.get('bio', ''),
                placeholder="简单介绍一下自己...",
                height=100
            )
            
            # 提交按钮
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.form_submit_button("保存更改", type="primary"):
                    profile_data = {
                        "full_name": full_name,
                        "company": company,
                        "job_title": job_title,
                        "phone": phone,
                        "bio": bio
                    }
                    
                    if update_profile(profile_data):
                        st.success("个人信息更新成功！")
                        st.rerun()
            
            with col2:
                if st.form_submit_button("重置"):
                    st.rerun()
    
    # 账户信息
    st.markdown("---")
    st.markdown("#### 账户信息")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**账户ID**: {user.get('id', 'N/A')}")
        st.markdown(f"**注册时间**: {user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A'}")
    
    with col2:
        st.markdown(f"**订阅计划**: {user.get('subscription_plan', 'free').title()}")
        st.markdown(f"**账户状态**: {'活跃' if user.get('is_active') else '停用'}")

    with col3:
        st.markdown(f"**最后登录**: {user.get('last_login', 'N/A')[:16] if user.get('last_login') else 'N/A'}")
        st.markdown(f"**邮箱验证**: {'已验证' if user.get('email_verified') else '未验证'}")

def render_app_settings():
    """渲染应用设置"""
    st.markdown("### 应用设置")
    
    # 界面设置
    st.markdown("#### 界面设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox(
            "主题模式",
            ["自动", "浅色", "深色"],
            index=0,
            help="选择应用的主题模式"
        )
        
        language = st.selectbox(
            "语言设置",
            ["中文", "English"],
            index=0,
            help="选择应用界面语言"
        )
    
    with col2:
        sidebar_default = st.selectbox(
            "侧边栏默认状态",
            ["展开", "收起"],
            index=0
        )
        
        page_size = st.number_input(
            "每页显示条数",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
            help="设置列表页面每页显示的记录数"
        )
    
    # 通知设置
    st.markdown("#### 通知设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_notifications = st.checkbox(
            "邮件通知",
            value=True,
            help="接收重要更新和检测完成通知"
        )
        
        detection_alerts = st.checkbox(
            "检测完成提醒",
            value=True,
            help="检测任务完成时发送通知"
        )
    
    with col2:
        weekly_report = st.checkbox(
            "周报推送",
            value=False,
            help="每周接收品牌分析报告"
        )
        
        system_updates = st.checkbox(
            "系统更新通知",
            value=True,
            help="接收系统功能更新通知"
        )
    
    # API设置
    st.markdown("#### API设置")
    
    config = get_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_timeout = st.number_input(
            "API超时时间(秒)",
            min_value=10,
            max_value=120,
            value=config.api_timeout,
            help="设置API请求的超时时间"
        )
    
    with col2:
        max_retries = st.number_input(
            "最大重试次数",
            min_value=1,
            max_value=10,
            value=config.max_retries,
            help="API请求失败时的最大重试次数"
        )
    
    # 保存设置
    if st.button("保存设置", type="primary"):
        settings_data = {
            "theme": theme,
            "language": language,
            "sidebar_default": sidebar_default,
            "page_size": page_size,
            "email_notifications": email_notifications,
            "detection_alerts": detection_alerts,
            "weekly_report": weekly_report,
            "system_updates": system_updates,
            "api_timeout": api_timeout,
            "max_retries": max_retries
        }
        
        if save_app_settings(settings_data):
            st.success("设置保存成功！")

def render_usage_stats():
    """渲染使用统计"""
    st.markdown("### 使用统计")
    
    # 获取使用统计数据
    stats_data = get_usage_statistics()
    
    # 总体统计
    st.markdown("#### 总体统计")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "总检测次数",
            stats_data.get('total_detections', 0),
            delta=f"+{stats_data.get('detections_this_month', 0)} (本月)"
        )
    
    with col2:
        st.metric(
            "创建项目数",
            stats_data.get('total_projects', 0),
            delta=f"+{stats_data.get('projects_this_month', 0)} (本月)"
        )
    
    with col3:
        st.metric(
            "监测品牌数",
            stats_data.get('total_brands', 0),
            delta=f"+{stats_data.get('brands_this_month', 0)} (本月)"
        )
    
    with col4:
        st.metric(
            "使用天数",
            stats_data.get('active_days', 0),
            delta=f"{stats_data.get('days_this_month', 0)} (本月)"
        )
    
    # 使用趋势
    st.markdown("#### 使用趋势")
    
    # 模拟趋势数据
    import pandas as pd
    import plotly.express as px
    
    trend_data = stats_data.get('usage_trend', [])
    
    if trend_data:
        df = pd.DataFrame(trend_data)
        
        fig = px.line(
            df,
            x='date',
            y='detections',
            title='每日检测次数趋势',
            labels={'detections': '检测次数', 'date': '日期'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # 功能使用情况
    st.markdown("#### 功能使用情况")
    
    feature_usage = stats_data.get('feature_usage', {})
    
    if feature_usage:
        col1, col2 = st.columns(2)
        
        with col1:
            # 功能使用次数
            feature_df = pd.DataFrame([
                {'功能': k, '使用次数': v} for k, v in feature_usage.items()
            ])
            
            st.dataframe(feature_df, use_container_width=True, hide_index=True)
        
        with col2:
            # 功能使用饼图
            fig = px.pie(
                feature_df,
                values='使用次数',
                names='功能',
                title='功能使用分布'
            )
            
            st.plotly_chart(fig, use_container_width=True)

def render_security_settings():
    """渲染安全设置"""
    st.markdown("### 安全设置")

    # 密码修改
    st.markdown("#### 修改密码")
    
    with st.form("change_password_form"):
        current_password = st.text_input(
            "当前密码",
            type="password",
            placeholder="请输入当前密码"
        )
        
        new_password = st.text_input(
            "新密码",
            type="password",
            placeholder="请输入新密码"
        )
        
        confirm_password = st.text_input(
            "确认新密码",
            type="password",
            placeholder="请再次输入新密码"
        )
        
        if st.form_submit_button("修改密码", type="primary"):
            if not all([current_password, new_password, confirm_password]):
                st.error("请填写完整信息")
            elif new_password != confirm_password:
                st.error("两次输入的新密码不一致")
            elif len(new_password) < 6:
                st.error("新密码长度至少6位")
            else:
                if change_password(current_password, new_password):
                    st.success("密码修改成功！")
    
    # 登录记录
    st.markdown("#### 登录记录")
    
    login_records = get_login_records()
    
    if login_records:
        login_df = pd.DataFrame(login_records)
        st.dataframe(login_df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无登录记录")
    
    # 安全选项
    st.markdown("#### 安全选项")
    
    col1, col2 = st.columns(2)
    
    with col1:
        two_factor_auth = st.checkbox(
            "启用双因素认证",
            value=False,
            help="增强账户安全性"
        )
        
        login_notifications = st.checkbox(
            "登录通知",
            value=True,
            help="新设备登录时发送邮件通知"
        )
    
    with col2:
        auto_logout = st.selectbox(
            "自动登出时间",
            ["1小时", "4小时", "8小时", "24小时", "永不"],
            index=2,
            help="设置无操作时的自动登出时间"
        )
        
        session_limit = st.number_input(
            "最大同时登录设备数",
            min_value=1,
            max_value=10,
            value=3,
            help="限制同时登录的设备数量"
        )
    
    # 账户操作
    st.markdown("---")
    st.markdown("#### 危险操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("重置所有设置"):
            if st.session_state.get("confirm_reset_settings", False):
                reset_all_settings()
                st.success("设置已重置")
                st.rerun()
            else:
                st.session_state.confirm_reset_settings = True
                st.warning("再次点击确认重置所有设置")
    
    with col2:
        if st.button("删除账户"):
            st.error("账户删除功能需要联系客服处理")

# 辅助函数
def update_profile(profile_data: Dict[str, Any]) -> bool:
    """更新个人资料"""
    try:
        auth_manager = AuthManager()
        return auth_manager.update_user_profile(profile_data)
    except Exception as e:
        st.error(f"更新失败: {str(e)}")
        return False

def save_app_settings(settings_data: Dict[str, Any]) -> bool:
    """保存应用设置"""
    try:
        # 保存到会话状态
        for key, value in settings_data.items():
            st.session_state[f"setting_{key}"] = value
        
        return True
    except Exception as e:
        st.error(f"保存设置失败: {str(e)}")
        return False

def get_usage_statistics() -> Dict[str, Any]:
    """获取使用统计"""
    # 模拟统计数据
    from datetime import datetime, timedelta
    import random
    
    # 生成趋势数据
    trend_data = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
        trend_data.append({
            'date': date,
            'detections': random.randint(0, 15)
        })
    
    return {
        'total_detections': 156,
        'detections_this_month': 45,
        'total_projects': 8,
        'projects_this_month': 2,
        'total_brands': 24,
        'brands_this_month': 6,
        'active_days': 45,
        'days_this_month': 18,
        'usage_trend': trend_data,
        'feature_usage': {
            '引用检测': 89,
            '项目管理': 34,
            '数据分析': 28,
            '模板管理': 15,
            '历史查看': 67
        }
    }

def change_password(current_password: str, new_password: str) -> bool:
    """修改密码"""
    try:
        # 这里应该调用API修改密码
        # 演示模式直接返回成功
        return True
    except Exception as e:
        st.error(f"修改密码失败: {str(e)}")
        return False

def get_login_records() -> List[Dict[str, Any]]:
    """获取登录记录"""
    # 模拟登录记录
    return [
        {
            '登录时间': '2024-12-19 14:30:25',
            '登录IP': '192.168.1.100',
            '设备信息': 'Chrome 120.0 / Windows 10',
            '登录状态': '成功'
        },
        {
            '登录时间': '2024-12-18 09:15:42',
            '登录IP': '192.168.1.100',
            '设备信息': 'Chrome 120.0 / Windows 10',
            '登录状态': '成功'
        }
    ]

def reset_all_settings():
    """重置所有设置"""
    # 清除设置相关的会话状态
    keys_to_remove = [key for key in st.session_state.keys() if key.startswith('setting_')]
    for key in keys_to_remove:
        del st.session_state[key]

if __name__ == "__main__":
    main()
