"""
侧边栏组件
应用导航和用户信息显示
"""

import streamlit as st
from components.auth import AuthManager
from utils.config import get_config, show_config_debug
from utils.session import show_session_debug

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # 应用标题和版本
        config = get_config()
        st.markdown(f"""
        # 🌍 {config.app_name}
        **{config.app_version}**
        
        *AI引用检测平台*
        """)
        
        st.markdown("---")
        
        # 用户信息
        render_user_info()
        
        st.markdown("---")
        
        # 导航菜单
        render_navigation()
        
        st.markdown("---")
        
        # 快速操作
        render_quick_actions()
        
        # 调试信息 (仅在调试模式下显示)
        if config.debug:
            st.markdown("---")
            render_debug_section()

def render_user_info():
    """渲染用户信息"""
    auth_manager = AuthManager()
    user = auth_manager.get_current_user()
    
    if user:
        st.markdown("### 👤 用户信息")
        
        # 用户头像和基本信息
        col1, col2 = st.columns([1, 2])
        with col1:
            # 使用用户名首字母作为头像
            initial = user.get('full_name', user.get('email', 'U'))[0].upper()
            st.markdown(f"""
            <div style="
                width: 50px; 
                height: 50px; 
                border-radius: 50%; 
                background: linear-gradient(45deg, #1f77b4, #ff7f0e);
                display: flex; 
                align-items: center; 
                justify-content: center; 
                color: white; 
                font-weight: bold; 
                font-size: 20px;
                margin: 0 auto;
            ">{initial}</div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            **{user.get('full_name', '用户')}**  
            {user.get('email', '')}  
            📊 {user.get('subscription_plan', 'free').title()}
            """)
        
        # 登出按钮
        if st.button("🚪 登出", key="logout_btn", use_container_width=True):
            auth_manager.logout()

def render_navigation():
    """渲染导航菜单"""
    st.markdown("### 📋 功能导航")
    
    # 主要功能页面
    pages = [
        {"name": "🏠 首页", "file": "main.py", "description": "概览和快速操作"},
        {"name": "📁 项目管理", "file": "pages/2_📁_Projects.py", "description": "管理检测项目"},
        {"name": "🔍 引用检测", "file": "pages/3_🔍_Detection.py", "description": "核心检测功能"},
        {"name": "📜 检测历史", "file": "pages/4_📜_History.py", "description": "历史记录查看"},
        {"name": "📚 模板管理", "file": "pages/5_📚_Templates.py", "description": "Prompt模板库"},
        {"name": "📊 数据分析", "file": "pages/6_📊_Analytics.py", "description": "可视化分析"},
        {"name": "👤 个人资料", "file": "pages/7_👤_Profile.py", "description": "用户设置"}
    ]
    
    for page in pages:
        if st.button(
            page["name"], 
            key=f"nav_{page['file']}", 
            help=page["description"],
            use_container_width=True
        ):
            if page["file"] == "main.py":
                st.switch_page("main.py")
            else:
                st.switch_page(page["file"])

def render_quick_actions():
    """渲染快速操作"""
    st.markdown("### ⚡ 快速操作")
    
    # 快速检测
    if st.button("🚀 快速检测", key="quick_detection", use_container_width=True, type="primary"):
        st.switch_page("pages/3_🔍_Detection.py")
    
    # 查看最新结果
    if st.button("📊 最新结果", key="latest_results", use_container_width=True):
        st.switch_page("pages/4_📜_History.py")
    
    # 创建新项目
    if st.button("➕ 新建项目", key="new_project", use_container_width=True):
        st.switch_page("pages/2_📁_Projects.py")

def render_current_project():
    """渲染当前项目信息"""
    current_project = st.session_state.get('current_project')
    
    if current_project:
        st.markdown("### 📁 当前项目")
        
        with st.container():
            st.markdown(f"""
            **{current_project.get('name', '未命名项目')}**  
            🌐 {current_project.get('domain', '')}  
            🏷️ {len(current_project.get('brands', []))} 个品牌  
            📅 {current_project.get('created_at', '')[:10] if current_project.get('created_at') else ''}
            """)
            
            if st.button("🔄 切换项目", key="switch_project", use_container_width=True):
                st.switch_page("pages/2_📁_Projects.py")
    else:
        st.markdown("### 📁 当前项目")
        st.info("未选择项目")
        
        if st.button("📁 选择项目", key="select_project", use_container_width=True):
            st.switch_page("pages/2_📁_Projects.py")

def render_system_status():
    """渲染系统状态"""
    st.markdown("### 🔧 系统状态")
    
    # API连接状态
    config = get_config()
    
    try:
        import httpx
        with httpx.Client(timeout=5) as client:
            response = client.get(f"{config.api_base_url.replace('/api/v1', '')}/health")
            if response.status_code == 200:
                st.success("🟢 API连接正常")
            else:
                st.warning("🟡 API响应异常")
    except:
        st.error("🔴 API连接失败")
    
    # 会话状态
    if st.session_state.authenticated:
        st.success("🟢 用户已认证")
    else:
        st.error("🔴 用户未认证")
    
    # 缓存状态
    cache_count = (
        len(st.session_state.get('projects_cache', {})) +
        len(st.session_state.get('templates_cache', {})) +
        len(st.session_state.get('history_cache', {}))
    )
    st.info(f"💾 缓存项目: {cache_count}")

def render_debug_section():
    """渲染调试部分"""
    st.markdown("### 🔍 调试信息")
    
    # 配置调试
    show_config_debug()
    
    # 会话调试
    show_session_debug()
    
    # 清除缓存按钮
    if st.button("🗑️ 清除缓存", key="clear_cache"):
        from utils.session import clear_cache
        clear_cache()
        st.success("✅ 缓存已清除")
        st.rerun()

def render_help_section():
    """渲染帮助部分"""
    with st.expander("❓ 帮助和支持", expanded=False):
        st.markdown("""
        ### 📖 使用指南
        
        1. **项目管理**: 创建和管理您的品牌监测项目
        2. **引用检测**: 输入Prompt，选择品牌和AI模型进行检测
        3. **结果分析**: 查看检测结果和数据可视化
        4. **历史记录**: 管理和分析历史检测数据
        5. **模板库**: 创建和使用Prompt模板提高效率
        
        ### 🆘 常见问题
        
        **Q: 如何开始第一次检测？**  
        A: 先创建项目，然后在引用检测页面输入Prompt和选择品牌。
        
        **Q: 支持哪些AI模型？**  
        A: 目前支持豆包、DeepSeek和OpenAI GPT模型。
        
        **Q: 检测结果如何解读？**  
        A: 查看提及率、置信度和上下文信息，数据分析页面有详细图表。
        
        ### 📞 联系支持
        
        - 📧 邮箱: support@geolens.ai
        - 🐛 问题反馈: [GitHub Issues](https://github.com/franksunye/GeoLens/issues)
        - 📚 文档: [项目文档](https://github.com/franksunye/GeoLens/docs)
        """)

# 在侧边栏底部添加帮助信息
def render_sidebar_footer():
    """渲染侧边栏底部"""
    st.markdown("---")
    
    # 帮助部分
    render_help_section()
    
    # 版权信息
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
        © 2024 GeoLens<br>
        AI引用检测平台
    </div>
    """, unsafe_allow_html=True)
