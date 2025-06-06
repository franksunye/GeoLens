"""
企业级UI组件库
提供专业、简洁的企业级用户界面组件
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Callable
import pandas as pd
from datetime import datetime

def render_metric_cards(metrics: List[Dict[str, Any]], columns: int = 4):
    """渲染指标卡片"""
    cols = st.columns(columns)
    
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            st.metric(
                label=metric.get('label', ''),
                value=metric.get('value', ''),
                delta=metric.get('delta'),
                help=metric.get('help')
            )

def render_action_buttons(actions: List[Dict[str, Any]], columns: int = 3):
    """渲染操作按钮组"""
    cols = st.columns(columns)
    
    results = {}
    for i, action in enumerate(actions):
        with cols[i % columns]:
            if st.button(
                action.get('label', ''),
                key=action.get('key'),
                type=action.get('type', 'secondary'),
                help=action.get('help'),
                use_container_width=True
            ):
                results[action.get('key', f'action_{i}')] = True
    
    return results

def render_info_card(title: str, content: str, icon: str = "ℹ️", 
                    card_type: str = "info"):
    """渲染信息卡片"""
    type_colors = {
        'info': '#e3f2fd',
        'success': '#e8f5e8',
        'warning': '#fff3e0',
        'error': '#ffebee'
    }
    
    color = type_colors.get(card_type, type_colors['info'])
    
    st.markdown(f"""
    <div style="
        background-color: {color};
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
    ">
        <h4>{icon} {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def render_data_table(data: List[Dict[str, Any]], 
                     title: Optional[str] = None,
                     searchable: bool = True,
                     sortable: bool = True,
                     actions: Optional[List[Dict[str, Any]]] = None):
    """渲染数据表格"""
    if title:
        st.markdown(f"#### {title}")
    
    if not data:
        st.info("📝 暂无数据")
        return {}
    
    df = pd.DataFrame(data)
    
    # 搜索功能
    if searchable:
        search_term = st.text_input("🔍 搜索", key=f"search_{id(data)}")
        if search_term:
            # 简单的文本搜索
            mask = df.astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            df = df[mask]
    
    # 显示表格
    selected_rows = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun" if actions else None,
        selection_mode="multi-row" if actions else None
    )
    
    # 操作按钮
    action_results = {}
    if actions and selected_rows and len(selected_rows.get('selection', {}).get('rows', [])) > 0:
        st.markdown("**选中行操作:**")
        action_results = render_action_buttons(actions)
        action_results['selected_rows'] = selected_rows['selection']['rows']
    
    return action_results

def render_form_section(title: str, fields: List[Dict[str, Any]], 
                       form_key: str, submit_label: str = "提交"):
    """渲染表单部分"""
    st.markdown(f"#### {title}")
    
    with st.form(form_key):
        form_data = {}
        
        for field in fields:
            field_type = field.get('type', 'text')
            field_key = field.get('key', '')
            field_label = field.get('label', '')
            field_value = field.get('value', '')
            field_options = field.get('options', [])
            field_help = field.get('help', '')
            
            if field_type == 'text':
                form_data[field_key] = st.text_input(
                    field_label, value=field_value, help=field_help
                )
            elif field_type == 'textarea':
                form_data[field_key] = st.text_area(
                    field_label, value=field_value, help=field_help,
                    height=field.get('height', 100)
                )
            elif field_type == 'number':
                form_data[field_key] = st.number_input(
                    field_label, value=field_value, help=field_help,
                    min_value=field.get('min_value'),
                    max_value=field.get('max_value'),
                    step=field.get('step', 1)
                )
            elif field_type == 'select':
                form_data[field_key] = st.selectbox(
                    field_label, options=field_options, 
                    index=field_options.index(field_value) if field_value in field_options else 0,
                    help=field_help
                )
            elif field_type == 'multiselect':
                form_data[field_key] = st.multiselect(
                    field_label, options=field_options, 
                    default=field_value if isinstance(field_value, list) else [],
                    help=field_help
                )
            elif field_type == 'checkbox':
                form_data[field_key] = st.checkbox(
                    field_label, value=bool(field_value), help=field_help
                )
            elif field_type == 'slider':
                form_data[field_key] = st.slider(
                    field_label, 
                    min_value=field.get('min_value', 0),
                    max_value=field.get('max_value', 100),
                    value=field_value or field.get('min_value', 0),
                    step=field.get('step', 1),
                    help=field_help
                )
        
        submitted = st.form_submit_button(submit_label, type="primary")
        
        if submitted:
            return form_data
    
    return None

def render_progress_indicator(current_step: int, total_steps: int, 
                            step_labels: Optional[List[str]] = None):
    """渲染进度指示器"""
    progress = current_step / total_steps
    st.progress(progress)
    
    if step_labels and len(step_labels) >= total_steps:
        cols = st.columns(total_steps)
        for i, label in enumerate(step_labels[:total_steps]):
            with cols[i]:
                if i < current_step:
                    st.markdown(f"✅ {label}")
                elif i == current_step:
                    st.markdown(f"🔄 **{label}**")
                else:
                    st.markdown(f"⏳ {label}")

def render_status_badge(status: str, status_config: Optional[Dict[str, Dict]] = None):
    """渲染状态徽章"""
    default_config = {
        'success': {'color': '#28a745', 'icon': '✅', 'text': '成功'},
        'warning': {'color': '#ffc107', 'icon': '⚠️', 'text': '警告'},
        'error': {'color': '#dc3545', 'icon': '❌', 'text': '错误'},
        'info': {'color': '#17a2b8', 'icon': 'ℹ️', 'text': '信息'},
        'pending': {'color': '#6c757d', 'icon': '⏳', 'text': '等待中'},
        'running': {'color': '#007bff', 'icon': '🔄', 'text': '运行中'}
    }
    
    config = status_config or default_config
    status_info = config.get(status, config.get('info', {}))
    
    st.markdown(f"""
    <span style="
        background-color: {status_info.get('color', '#17a2b8')};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    ">
        {status_info.get('icon', 'ℹ️')} {status_info.get('text', status)}
    </span>
    """, unsafe_allow_html=True)

def render_loading_spinner(message: str = "加载中..."):
    """渲染加载动画"""
    with st.spinner(message):
        return st.empty()

def render_confirmation_dialog(message: str, confirm_key: str, 
                             confirm_label: str = "确认", 
                             cancel_label: str = "取消"):
    """渲染确认对话框"""
    st.warning(message)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(confirm_label, key=f"{confirm_key}_confirm", type="primary"):
            return True
    
    with col2:
        if st.button(cancel_label, key=f"{confirm_key}_cancel"):
            return False
    
    return None

def render_file_uploader(label: str, file_types: List[str], 
                        max_size_mb: int = 10, multiple: bool = False):
    """渲染文件上传器"""
    uploaded_files = st.file_uploader(
        label,
        type=file_types,
        accept_multiple_files=multiple,
        help=f"支持格式: {', '.join(file_types)}，最大文件大小: {max_size_mb}MB"
    )
    
    if uploaded_files:
        if not multiple:
            uploaded_files = [uploaded_files]
        
        valid_files = []
        for file in uploaded_files:
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                st.error(f"文件 {file.name} 超过大小限制 ({file_size_mb:.1f}MB > {max_size_mb}MB)")
            else:
                valid_files.append(file)
        
        return valid_files if multiple else (valid_files[0] if valid_files else None)
    
    return None

def render_tabs_with_content(tabs_config: List[Dict[str, Any]]):
    """渲染带内容的选项卡"""
    tab_labels = [tab.get('label', f'Tab {i+1}') for i, tab in enumerate(tabs_config)]
    tabs = st.tabs(tab_labels)
    
    for i, (tab, config) in enumerate(zip(tabs, tabs_config)):
        with tab:
            content_func = config.get('content_func')
            if content_func and callable(content_func):
                content_func()
            else:
                content = config.get('content', '')
                if content:
                    st.markdown(content)

def render_expandable_section(title: str, content_func: Callable, 
                            expanded: bool = False, icon: str = ""):
    """渲染可展开部分"""
    with st.expander(f"{icon} {title}", expanded=expanded):
        if callable(content_func):
            content_func()

def render_sidebar_section(title: str, content_func: Callable):
    """渲染侧边栏部分"""
    with st.sidebar:
        st.markdown(f"### {title}")
        if callable(content_func):
            content_func()
        st.markdown("---")

def show_success_message(message: str, duration: int = 3):
    """显示成功消息"""
    success_placeholder = st.success(message)
    # 注意：Streamlit中无法自动清除消息，需要用户交互
    return success_placeholder

def show_error_message(message: str, details: Optional[str] = None):
    """显示错误消息"""
    st.error(message)
    if details:
        with st.expander("错误详情"):
            st.text(details)

def render_key_value_pairs(data: Dict[str, Any], title: Optional[str] = None):
    """渲染键值对"""
    if title:
        st.markdown(f"#### {title}")
    
    for key, value in data.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{key}:**")
        with col2:
            st.markdown(str(value))

def render_timeline(events: List[Dict[str, Any]]):
    """渲染时间线"""
    for i, event in enumerate(events):
        timestamp = event.get('timestamp', '')
        title = event.get('title', '')
        description = event.get('description', '')
        status = event.get('status', 'info')
        
        # 时间线连接线
        if i > 0:
            st.markdown("│")
        
        # 事件节点
        col1, col2 = st.columns([1, 4])
        with col1:
            render_status_badge(status)
        with col2:
            st.markdown(f"**{title}**")
            if description:
                st.markdown(description)
            if timestamp:
                st.caption(timestamp)
