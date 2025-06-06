"""
GeoLens Streamlit MVP - 主应用入口
AI引用检测平台前端应用
"""

import streamlit as st
import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from components.auth import AuthManager
from components.sidebar import render_sidebar
from utils.config import load_config, get_config
from utils.session import init_session_state
from utils.error_handler import error_handler, handle_error, show_error_dashboard
from utils.performance_monitor import monitor_page_load, show_performance_dashboard
from utils.cache_manager import cache_stats

# 页面配置
st.set_page_config(
    page_title="GeoLens - AI引用检测平台",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/franksunye/GeoLens',
        'Report a bug': 'https://github.com/franksunye/GeoLens/issues',
        'About': """
        # GeoLens AI引用检测平台
        
        专注于品牌在生成式AI中的引用检测和可见性分析
        
        **版本**: v0.8.0-streamlit-mvp
        **技术栈**: Streamlit + FastAPI + Python
        """
    }
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主题色彩 */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --warning-color: #d62728;
        --info-color: #17becf;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 自定义标题样式 */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        border-bottom: 2px solid var(--primary-color);
    }
    
    /* 卡片样式 */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary-color);
    }
    
    /* 成功消息样式 */
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    
    /* 警告消息样式 */
    .warning-message {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* 按钮样式 */
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

@error_handler(context={"page": "login"})
def show_login_page():
    """显示登录页面"""
    st.markdown('<div class="main-header">🌍 GeoLens AI引用检测平台</div>', unsafe_allow_html=True)
    
    # 产品介绍
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### 🎯 专业的AI引用检测平台
        
        **核心功能**:
        - 🔍 **多模型引用检测**: 支持豆包、DeepSeek、ChatGPT等主流AI模型
        - 📊 **智能数据分析**: 品牌提及率、置信度分析、竞品对比
        - 📈 **可视化报告**: 直观的图表展示和趋势分析
        - 💾 **历史记录管理**: 完整的检测历史和模板库
        
        **适用场景**:
        - 品牌在AI中的曝光监测
        - 竞品分析和市场洞察  
        - AI可见性优化策略
        - 客户诊断报告生成
        """)
        
        # 登录表单
        st.markdown("---")
        st.markdown("### 🔐 用户登录")
        
        with st.form("login_form"):
            email = st.text_input("📧 邮箱地址", placeholder="请输入您的邮箱")
            password = st.text_input("🔒 密码", type="password", placeholder="请输入密码")
            
            col_login, col_register = st.columns(2)
            with col_login:
                login_button = st.form_submit_button("🚀 登录", type="primary")
            with col_register:
                register_button = st.form_submit_button("📝 注册")
        
        # 处理登录
        if login_button:
            handle_login_attempt(email, password)

        # 处理注册
        if register_button:
            handle_register_attempt()
        
        # 演示账号
        render_demo_account_info()

def handle_login_attempt(email: str, password: str):
    """处理登录尝试"""
    if email and password:
        auth_manager = AuthManager()
        if auth_manager.login(email, password):
            st.success("✅ 登录成功！正在跳转...")
            st.rerun()
        else:
            st.error("❌ 登录失败，请检查邮箱和密码")
    else:
        st.warning("⚠️ 请填写完整的登录信息")

def handle_register_attempt():
    """处理注册尝试"""
    st.info("📝 注册功能开发中，请联系管理员获取账号")

def render_demo_account_info():
    """渲染演示账号信息"""
    st.markdown("---")
    st.markdown("### 🎮 演示账号")
    st.info("""
    **演示邮箱**: demo@geolens.ai
    **演示密码**: demo123

    *注意: 这是演示账号，数据仅供测试使用*
    """)

@error_handler(context={"page": "dashboard"})
def show_main_app():
    """显示主应用"""
    # 监控页面加载性能
    monitor_page_load()

    # 渲染侧边栏
    render_sidebar()

    # 主内容区域
    st.markdown('<div class="main-header">🌍 GeoLens Dashboard</div>', unsafe_allow_html=True)
    
    # 欢迎信息
    user_info = st.session_state.get('user', {})
    user_name = user_info.get('full_name', user_info.get('email', '用户'))
    
    st.markdown(f"""
    ### 👋 欢迎回来，{user_name}！
    
    这是您的AI引用检测控制台。您可以通过左侧导航栏访问各项功能：
    """)
    
    # 快速统计
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 总检测次数",
            value="156",
            delta="12 (本周)"
        )
    
    with col2:
        st.metric(
            label="🏷️ 监测品牌",
            value="8",
            delta="2 (新增)"
        )
    
    with col3:
        st.metric(
            label="🤖 AI模型",
            value="3",
            delta="豆包+DeepSeek+GPT"
        )
    
    with col4:
        st.metric(
            label="📈 平均提及率",
            value="23.5%",
            delta="5.2% (上升)"
        )
    
    # 快速操作
    st.markdown("---")
    st.markdown("### 🚀 快速操作")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 开始新检测", type="primary"):
            st.switch_page("pages/3_🔍_Detection.py")
    
    with col2:
        if st.button("📊 查看分析报告"):
            st.switch_page("pages/6_📊_Analytics.py")
    
    with col3:
        if st.button("📜 检测历史"):
            st.switch_page("pages/4_📜_History.py")
    
    # 最近活动
    st.markdown("---")
    st.markdown("### 📋 最近活动")
    
    # 模拟最近活动数据
    import pandas as pd
    from datetime import datetime, timedelta
    
    recent_activities = pd.DataFrame({
        '时间': [
            datetime.now() - timedelta(hours=2),
            datetime.now() - timedelta(hours=5),
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
        ],
        '活动': [
            '完成品牌检测: Notion vs Obsidian',
            '创建新项目: SaaS工具监测',
            '导出检测报告: 团队协作工具分析',
            '更新Prompt模板: 笔记软件推荐',
        ],
        '状态': ['✅ 成功', '✅ 成功', '✅ 成功', '✅ 成功'],
        '结果': ['提及率: 45%', '项目创建完成', '报告已下载', '模板已保存']
    })
    
    st.dataframe(
        recent_activities,
        use_container_width=True,
        hide_index=True
    )

def main():
    """主函数"""
    try:
        # 初始化会话状态
        init_session_state()

        # 加载配置
        config = load_config()

        # 检查认证状态
        auth_manager = AuthManager()

        # 调试模式显示额外信息
        if config.debug:
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 🔧 调试信息")

                # 性能监控
                if st.checkbox("显示性能监控", key="show_perf"):
                    show_performance_dashboard()

                # 错误监控
                if st.checkbox("显示错误监控", key="show_errors"):
                    show_error_dashboard()

                # 缓存统计
                if st.checkbox("显示缓存统计", key="show_cache"):
                    st.markdown("#### 📊 缓存统计")
                    stats = cache_stats()
                    st.json(stats)

        if not auth_manager.is_authenticated():
            show_login_page()
        else:
            show_main_app()

    except Exception as e:
        handle_error(e, context={"page": "main", "function": "main"})

if __name__ == "__main__":
    main()
