"""
项目管理页面
管理检测项目和品牌列表
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from components.auth import require_auth
from components.sidebar import render_sidebar
from services.api_client import SyncAPIClient
from utils.session import set_current_project, get_current_project, update_cache, get_cache

# 页面配置
st.set_page_config(
    page_title="项目管理 - GeoLens",
    page_icon="📁",
    layout="wide"
)

@require_auth
def main():
    """主函数"""
    render_sidebar()
    
    st.markdown("# 📁 项目管理")
    st.markdown("创建和管理您的品牌监测项目")
    
    # 主要功能选项卡
    tab1, tab2, tab3 = st.tabs(["📋 项目列表", "➕ 创建项目", "⚙️ 项目设置"])
    
    with tab1:
        render_projects_list()
    
    with tab2:
        render_create_project()
    
    with tab3:
        render_project_settings()

def render_projects_list():
    """渲染项目列表"""
    st.markdown("### 📋 我的项目")
    
    # 获取项目列表
    projects = get_projects_list()
    
    if not projects:
        st.info("📝 您还没有创建任何项目")
        if st.button("🚀 创建第一个项目", type="primary"):
            st.switch_page("pages/2_📁_Projects.py")
        return
    
    # 搜索和筛选
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 搜索项目", placeholder="输入项目名称或域名")
    
    with col2:
        status_filter = st.selectbox("📊 状态筛选", ["全部", "活跃", "暂停"])
    
    with col3:
        sort_by = st.selectbox("📅 排序方式", ["创建时间", "名称", "最后更新"])
    
    # 筛选项目
    filtered_projects = filter_projects(projects, search_term, status_filter)
    
    # 显示项目卡片
    if filtered_projects:
        for i in range(0, len(filtered_projects), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(filtered_projects):
                    render_project_card(filtered_projects[i])
            
            with col2:
                if i + 1 < len(filtered_projects):
                    render_project_card(filtered_projects[i + 1])
    else:
        st.info("🔍 没有找到匹配的项目")

def render_project_card(project: Dict[str, Any]):
    """渲染项目卡片"""
    with st.container():
        # 项目状态指示器
        status_color = "🟢" if project.get('is_active', True) else "🔴"
        
        st.markdown(f"""
        <div style="
            border: 1px solid #ddd; 
            border-radius: 10px; 
            padding: 20px; 
            margin: 10px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h4>{status_color} {project.get('name', '未命名项目')}</h4>
            <p><strong>🌐 域名:</strong> {project.get('domain', '未设置')}</p>
            <p><strong>📝 描述:</strong> {project.get('description', '暂无描述')[:100]}...</p>
            <p><strong>🏷️ 品牌数量:</strong> {len(project.get('brands', []))} 个</p>
            <p><strong>📅 创建时间:</strong> {project.get('created_at', '')[:10]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 操作按钮
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🎯 选择", key=f"select_{project['id']}", type="primary"):
                set_current_project(project)
                st.success(f"✅ 已选择项目: {project['name']}")
                st.rerun()
        
        with col2:
            if st.button("🔍 检测", key=f"detect_{project['id']}"):
                set_current_project(project)
                st.switch_page("pages/3_🔍_Detection.py")
        
        with col3:
            if st.button("✏️ 编辑", key=f"edit_{project['id']}"):
                st.session_state.editing_project = project
                st.rerun()
        
        with col4:
            if st.button("🗑️ 删除", key=f"delete_{project['id']}"):
                if st.session_state.get(f"confirm_delete_{project['id']}", False):
                    delete_project(project['id'])
                    st.rerun()
                else:
                    st.session_state[f"confirm_delete_{project['id']}"] = True
                    st.warning("⚠️ 再次点击确认删除")

def render_create_project():
    """渲染创建项目表单"""
    st.markdown("### ➕ 创建新项目")
    
    with st.form("create_project_form"):
        # 基本信息
        st.markdown("#### 📋 基本信息")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "📝 项目名称 *",
                placeholder="例如: SaaS工具监测",
                help="为您的监测项目起一个有意义的名称"
            )
        
        with col2:
            project_domain = st.text_input(
                "🌐 相关域名",
                placeholder="例如: saas-tools.com",
                help="与项目相关的网站域名（可选）"
            )
        
        project_description = st.text_area(
            "📝 项目描述",
            placeholder="描述这个项目的目标和用途...",
            height=100,
            help="详细描述项目的监测目标和用途"
        )
        
        # 品牌配置
        st.markdown("#### 🏷️ 品牌配置")
        
        # 预设品牌类别
        brand_categories = {
            "笔记软件": ["Notion", "Obsidian", "Roam Research", "Logseq", "RemNote"],
            "团队协作": ["Slack", "Teams", "Discord", "Zoom", "Miro"],
            "设计工具": ["Figma", "Sketch", "Adobe XD", "Canva", "Framer"],
            "开发工具": ["GitHub", "GitLab", "VS Code", "IntelliJ", "Docker"],
            "项目管理": ["Asana", "Trello", "Monday", "Jira", "Linear"]
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_category = st.selectbox(
                "📂 选择品牌类别",
                options=["自定义"] + list(brand_categories.keys()),
                help="选择预设的品牌类别或自定义"
            )
        
        with col2:
            if selected_category != "自定义":
                preset_brands = brand_categories[selected_category]
                selected_brands = st.multiselect(
                    "🏷️ 选择品牌",
                    options=preset_brands,
                    default=preset_brands[:3],
                    help="从预设列表中选择要监测的品牌"
                )
            else:
                selected_brands = []
        
        # 自定义品牌输入
        custom_brands_text = st.text_area(
            "✏️ 自定义品牌（每行一个）",
            placeholder="Brand A\nBrand B\nBrand C",
            help="输入自定义品牌名称，每行一个"
        )
        
        # 处理自定义品牌
        custom_brands = []
        if custom_brands_text.strip():
            custom_brands = [brand.strip() for brand in custom_brands_text.split('\n') if brand.strip()]
        
        # 合并品牌列表
        all_brands = list(set(selected_brands + custom_brands))
        
        if all_brands:
            st.markdown("**📋 将要监测的品牌:**")
            st.write(", ".join(all_brands))
        
        # 高级设置
        with st.expander("⚙️ 高级设置", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                industry = st.selectbox(
                    "🏢 行业分类",
                    options=["科技", "教育", "金融", "医疗", "零售", "其他"]
                )
            
            with col2:
                is_active = st.checkbox("🟢 项目激活", value=True)
        
        # 提交按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("🚀 创建项目", type="primary")
    
    # 处理表单提交
    if submit_button:
        if not project_name.strip():
            st.error("❌ 请输入项目名称")
            return
        
        if not all_brands:
            st.error("❌ 请至少添加一个品牌")
            return
        
        # 创建项目
        project_data = {
            "name": project_name.strip(),
            "domain": project_domain.strip(),
            "description": project_description.strip(),
            "brands": all_brands,
            "industry": industry,
            "is_active": is_active
        }
        
        if create_project(project_data):
            st.success("🎉 项目创建成功！")
            st.balloons()
            
            # 清除表单
            st.rerun()

def render_project_settings():
    """渲染项目设置"""
    current_project = get_current_project()
    
    if not current_project:
        st.info("⚠️ 请先选择一个项目")
        return
    
    st.markdown(f"### ⚙️ 项目设置: {current_project['name']}")
    
    # 编辑项目信息
    with st.form("edit_project_form"):
        st.markdown("#### 📝 基本信息")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("项目名称", value=current_project.get('name', ''))
        
        with col2:
            new_domain = st.text_input("相关域名", value=current_project.get('domain', ''))
        
        new_description = st.text_area(
            "项目描述", 
            value=current_project.get('description', ''),
            height=100
        )
        
        # 品牌管理
        st.markdown("#### 🏷️ 品牌管理")
        
        current_brands = current_project.get('brands', [])
        
        # 显示当前品牌
        if current_brands:
            st.markdown("**当前品牌:**")
            brands_df = pd.DataFrame({
                '品牌名称': current_brands,
                '状态': ['✅ 活跃'] * len(current_brands)
            })
            st.dataframe(brands_df, hide_index=True)
        
        # 添加新品牌
        new_brands_text = st.text_area(
            "添加新品牌（每行一个）",
            placeholder="New Brand A\nNew Brand B"
        )
        
        # 项目状态
        st.markdown("#### 📊 项目状态")
        new_is_active = st.checkbox(
            "项目激活", 
            value=current_project.get('is_active', True)
        )
        
        # 提交按钮
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 保存更改", type="primary"):
                # 处理新品牌
                new_brands = []
                if new_brands_text.strip():
                    new_brands = [brand.strip() for brand in new_brands_text.split('\n') if brand.strip()]
                
                updated_brands = list(set(current_brands + new_brands))
                
                # 更新项目数据
                updated_project = {
                    **current_project,
                    "name": new_name,
                    "domain": new_domain,
                    "description": new_description,
                    "brands": updated_brands,
                    "is_active": new_is_active
                }
                
                if update_project(current_project['id'], updated_project):
                    set_current_project(updated_project)
                    st.success("✅ 项目更新成功！")
                    st.rerun()
        
        with col2:
            if st.form_submit_button("🗑️ 删除项目", type="secondary"):
                if st.session_state.get("confirm_project_delete", False):
                    if delete_project(current_project['id']):
                        set_current_project(None)
                        st.success("✅ 项目删除成功！")
                        st.rerun()
                else:
                    st.session_state.confirm_project_delete = True
                    st.warning("⚠️ 再次点击确认删除")

# 辅助函数
def get_projects_list() -> List[Dict[str, Any]]:
    """获取项目列表"""
    try:
        api_client = SyncAPIClient()
        response = api_client.get("projects")
        return response.get("data", {}).get("items", [])
    except Exception as e:
        st.error(f"获取项目列表失败: {str(e)}")
        return []

def filter_projects(projects: List[Dict[str, Any]], search_term: str, status_filter: str) -> List[Dict[str, Any]]:
    """筛选项目"""
    filtered = projects
    
    # 搜索筛选
    if search_term:
        filtered = [
            p for p in filtered 
            if search_term.lower() in p.get('name', '').lower() 
            or search_term.lower() in p.get('domain', '').lower()
        ]
    
    # 状态筛选
    if status_filter == "活跃":
        filtered = [p for p in filtered if p.get('is_active', True)]
    elif status_filter == "暂停":
        filtered = [p for p in filtered if not p.get('is_active', True)]
    
    return filtered

def create_project(project_data: Dict[str, Any]) -> bool:
    """创建项目"""
    try:
        api_client = SyncAPIClient()
        response = api_client.post("projects", data=project_data)
        
        # 清除项目缓存
        from utils.session import clear_cache
        clear_cache("projects")
        
        return True
    except Exception as e:
        st.error(f"创建项目失败: {str(e)}")
        return False

def update_project(project_id: str, project_data: Dict[str, Any]) -> bool:
    """更新项目"""
    try:
        api_client = SyncAPIClient()
        response = api_client.put(f"projects/{project_id}", data=project_data)
        
        # 清除项目缓存
        from utils.session import clear_cache
        clear_cache("projects")
        
        return True
    except Exception as e:
        st.error(f"更新项目失败: {str(e)}")
        return False

def delete_project(project_id: str) -> bool:
    """删除项目"""
    try:
        api_client = SyncAPIClient()
        response = api_client.delete(f"projects/{project_id}")
        
        # 清除项目缓存
        from utils.session import clear_cache
        clear_cache("projects")
        
        return True
    except Exception as e:
        st.error(f"删除项目失败: {str(e)}")
        return False

if __name__ == "__main__":
    main()
