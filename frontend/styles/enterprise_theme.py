"""
企业级UI主题配置
参考Vercel、Salesforce等企业级应用的设计风格
"""

import streamlit as st

def apply_enterprise_theme():
    """应用企业级主题样式"""
    st.markdown("""
    <style>
        /* 企业级色彩系统 */
        :root {
            /* 主色调 - 冷色调为主 */
            --primary-color: #1f2937;
            --primary-light: #374151;
            --primary-dark: #111827;
            
            /* 次要色彩 */
            --secondary-color: #6b7280;
            --accent-color: #3b82f6;
            --accent-light: #60a5fa;
            
            /* 状态色彩 */
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --info-color: #3b82f6;
            
            /* 背景色彩 */
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --bg-dark: #0f172a;
            
            /* 边框色彩 */
            --border-light: #e2e8f0;
            --border-medium: #cbd5e1;
            --border-dark: #64748b;
            
            /* 文字色彩 */
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --text-inverse: #ffffff;
        }
        
        /* 隐藏Streamlit默认元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* 全局字体和基础样式 */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* 企业级标题样式 */
        .enterprise-header {
            font-size: 2rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }
        
        .enterprise-subheader {
            font-size: 1.125rem;
            font-weight: 400;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }
        
        /* 卡片样式 */
        .enterprise-card {
            background: var(--bg-primary);
            border: 1px solid var(--border-light);
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            transition: all 0.2s ease;
        }
        
        .enterprise-card:hover {
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            border-color: var(--border-medium);
        }
        
        /* 指标卡片 */
        .metric-card {
            background: var(--bg-primary);
            border: 1px solid var(--border-light);
            border-radius: 0.5rem;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        
        .metric-label {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .metric-delta {
            font-size: 0.75rem;
            font-weight: 500;
            margin-top: 0.25rem;
        }
        
        .metric-delta.positive {
            color: var(--success-color);
        }
        
        .metric-delta.negative {
            color: var(--error-color);
        }
        
        /* 按钮样式重写 */
        .stButton > button {
            background: var(--bg-primary);
            border: 1px solid var(--border-light);
            border-radius: 0.375rem;
            color: var(--text-primary);
            font-weight: 500;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            background: var(--bg-secondary);
            border-color: var(--border-medium);
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        }
        
        /* 主要按钮 */
        .stButton > button[kind="primary"] {
            background: var(--primary-color);
            border-color: var(--primary-color);
            color: var(--text-inverse);
        }
        
        .stButton > button[kind="primary"]:hover {
            background: var(--primary-light);
            border-color: var(--primary-light);
        }
        
        /* 状态指示器 */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .status-badge.success {
            background: rgb(16 185 129 / 0.1);
            color: var(--success-color);
        }
        
        .status-badge.warning {
            background: rgb(245 158 11 / 0.1);
            color: var(--warning-color);
        }
        
        .status-badge.error {
            background: rgb(239 68 68 / 0.1);
            color: var(--error-color);
        }
        
        .status-badge.info {
            background: rgb(59 130 246 / 0.1);
            color: var(--info-color);
        }
    </style>
    """, unsafe_allow_html=True)

def render_enterprise_header(title: str, subtitle: str = ""):
    """渲染企业级页面标题"""
    st.markdown(f"""
    <div class="enterprise-header">{title}</div>
    {f'<div class="enterprise-subheader">{subtitle}</div>' if subtitle else ''}
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, delta: str = "", delta_type: str = "neutral"):
    """渲染企业级指标卡片"""
    delta_class = f"metric-delta {delta_type}" if delta else ""
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ""
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_status_badge(status: str, text: str = ""):
    """渲染状态徽章"""
    display_text = text or status.title()
    st.markdown(f"""
    <span class="status-badge {status}">{display_text}</span>
    """, unsafe_allow_html=True)

def render_enterprise_card(content: str, title: str = ""):
    """渲染企业级卡片"""
    title_html = f"<h4>{title}</h4>" if title else ""
    st.markdown(f"""
    <div class="enterprise-card">
        {title_html}
        {content}
    </div>
    """, unsafe_allow_html=True)
