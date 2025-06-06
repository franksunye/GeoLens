from styles.enterprise_theme import apply_enterprise_theme, render_enterprise_header, render_status_badge
"""
模板管理页面
管理Prompt模板库
"""

import streamlit as st
import re
from typing import List, Dict, Any

from components.auth import require_auth
from components.sidebar import render_sidebar
from services.detection_service import TemplateService

# 页面配置
st.set_page_config(
    page_title="模板管理 - GeoLens",
    page_icon="📚",
    layout="wide"
)

# 应用企业级主题
apply_enterprise_theme()

@require_auth
def main():
    """主函数"""
    render_sidebar()
    
    render_enterprise_header("Prompt模板管理", "")
    st.markdown("创建和管理可复用的Prompt模板，提高检测效率")
    
    # 主要功能选项卡
    tab1, tab2, tab3 = st.tabs(["模板库", "创建模板", "模板编辑器"])
    
    with tab1:
        render_templates_library()
    
    with tab2:
        render_create_template()
    
    with tab3:
        render_template_editor()

def render_templates_library():
    """渲染模板库"""
    st.markdown("### 模板库")
    
    # 筛选控件
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox(
            "分类筛选",
            ["全部", "笔记软件", "团队协作", "设计工具", "开发工具", "自定义"]
        )
    
    with col2:
        search_term = st.text_input("搜索模板", placeholder="输入模板名称或关键词")
    
    with col3:
        sort_by = st.selectbox("排序方式", ["使用次数", "创建时间", "名称"])
    
    # 获取模板列表
    templates = get_templates_list(category_filter, search_term)
    
    if not templates:
        st.info("暂无模板，创建第一个模板吧！")
        if st.button("创建模板"):
            st.rerun()
        return
    
    # 显示模板卡片
    for template in templates:
        render_template_card(template)

def render_template_card(template: Dict[str, Any]):
    """渲染模板卡片"""
    with st.expander(f"{template.get('name', '未命名模板')}", expanded=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**分类**: {template.get('category', '未分类')}")
            st.markdown(f"**描述**: {template.get('description', '暂无描述')}")
            st.markdown(f"**使用次数**: {template.get('usage_count', 0)}")
            
            # 模板内容预览
            template_text = template.get('template', '')
            if len(template_text) > 100:
                preview_text = template_text[:100] + "..."
            else:
                preview_text = template_text
            
            st.markdown("**模板内容**:")
            st.code(preview_text, language="text")
            
            # 变量列表
            variables = template.get('variables', [])
            if variables:
                st.markdown(f"**变量**: {', '.join(['{' + var + '}' for var in variables])}")
        
        with col2:
            # 操作按钮
            if st.button("使用模板", key=f"use_{template['id']}"):
                use_template(template)
            
            if st.button("编辑", key=f"edit_{template['id']}"):
                st.session_state.editing_template = template
                st.rerun()
            
            if st.button("复制", key=f"copy_{template['id']}"):
                copy_template(template)
            
            if st.button("删除", key=f"delete_{template['id']}"):
                delete_template(template['id'])

def render_create_template():
    """渲染创建模板表单"""
    st.markdown("### 创建新模板")
    
    with st.form("create_template_form"):
        # 基本信息
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input(
                "模板名称 *",
                placeholder="例如: 笔记软件推荐模板"
            )
        
        with col2:
            template_category = st.selectbox(
                "模板分类 *",
                ["笔记软件", "团队协作", "设计工具", "开发工具", "自定义"]
            )
        
        template_description = st.text_area(
            "模板描述",
            placeholder="描述这个模板的用途和适用场景...",
            height=80
        )
        
        # 模板内容
        st.markdown("#### 模板内容")
        
        template_content = st.text_area(
            "Prompt模板 *",
            placeholder="推荐几个好用的{category}工具，要求{requirement}",
            height=150,
            help="使用 {变量名} 格式定义变量，例如: {category}, {requirement}"
        )
        
        # 自动提取变量
        if template_content:
            variables = extract_variables(template_content)
            if variables:
                st.markdown("**检测到的变量**:")
                st.write(", ".join([f"`{{{var}}}`" for var in variables]))
        
        # 高级设置
        with st.expander("高级设置", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                is_public = st.checkbox("公开模板", help="允许其他用户使用此模板")
            
            with col2:
                tags = st.text_input("标签", placeholder="标签1, 标签2, 标签3")
        
        # 提交按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("创建模板", type="primary")
    
    # 处理表单提交
    if submit_button:
        if not template_name.strip():
            st.error("请输入模板名称")
            return
        
        if not template_content.strip():
            st.error("请输入模板内容")
            return
        
        # 创建模板
        template_data = {
            "name": template_name.strip(),
            "category": template_category,
            "description": template_description.strip(),
            "template": template_content.strip(),
            "variables": extract_variables(template_content),
            "is_public": is_public,
            "tags": [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        }
        
        if create_template(template_data):
            st.success("模板创建成功！")
            st.rerun()

def render_template_editor():
    """渲染模板编辑器"""
    st.markdown("### 模板编辑器")
    
    # 检查是否有编辑中的模板
    editing_template = st.session_state.get('editing_template')
    
    if not editing_template:
        st.info("请从模板库中选择要编辑的模板")
        return
    
    st.markdown(f"**编辑模板**: {editing_template['name']}")
    
    with st.form("edit_template_form"):
        # 基本信息
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("模板名称", value=editing_template.get('name', ''))
        
        with col2:
            new_category = st.selectbox(
                "模板分类",
                ["笔记软件", "团队协作", "设计工具", "开发工具", "自定义"],
                index=["笔记软件", "团队协作", "设计工具", "开发工具", "自定义"].index(
                    editing_template.get('category', '自定义')
                )
            )
        
        new_description = st.text_area(
            "模板描述",
            value=editing_template.get('description', ''),
            height=80
        )
        
        # 模板内容
        new_content = st.text_area(
            "Prompt模板",
            value=editing_template.get('template', ''),
            height=150
        )
        
        # 变量预览
        if new_content:
            variables = extract_variables(new_content)
            if variables:
                st.markdown("**变量列表**:")
                st.write(", ".join([f"`{{{var}}}`" for var in variables]))
        
        # 模板测试
        st.markdown("#### 🧪 模板测试")
        
        if new_content and extract_variables(new_content):
            test_variables = {}
            variables = extract_variables(new_content)
            
            col_count = min(len(variables), 3)
            cols = st.columns(col_count)
            
            for i, var in enumerate(variables):
                with cols[i % col_count]:
                    test_variables[var] = st.text_input(
                        f"变量 {{{var}}}",
                        key=f"test_var_{var}",
                        placeholder=f"输入{var}的值"
                    )
            
            # 生成测试结果
            if all(test_variables.values()):
                test_result = new_content
                for var, value in test_variables.items():
                    test_result = test_result.replace(f"{{{var}}}", value)
                
                st.markdown("**测试结果**:")
                st.code(test_result, language="text")
        
        # 提交按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.form_submit_button("保存更改", type="primary"):
                updated_template = {
                    "name": new_name,
                    "category": new_category,
                    "description": new_description,
                    "template": new_content,
                    "variables": extract_variables(new_content)
                }
                
                if update_template(editing_template['id'], updated_template):
                    st.success("模板更新成功！")
                    st.session_state.editing_template = None
                    st.rerun()
        
        with col2:
            if st.form_submit_button("取消编辑"):
                st.session_state.editing_template = None
                st.rerun()
        
        with col3:
            if st.form_submit_button("删除模板"):
                if delete_template(editing_template['id']):
                    st.session_state.editing_template = None
                    st.rerun()

# 辅助函数
def extract_variables(template_text: str) -> List[str]:
    """提取模板变量"""
    variables = re.findall(r'\{(\w+)\}', template_text)
    return list(set(variables))  # 去重

def get_templates_list(category_filter: str, search_term: str) -> List[Dict[str, Any]]:
    """获取模板列表"""
    try:
        template_service = TemplateService()
        
        # 构建查询参数
        params = {}
        if category_filter != "全部":
            params['category'] = category_filter
        
        response = template_service.get_templates(**params)
        templates = response.get("data", [])
        
        # 搜索筛选
        if search_term:
            templates = [
                t for t in templates
                if search_term.lower() in t.get('name', '').lower()
                or search_term.lower() in t.get('description', '').lower()
            ]
        
        return templates
        
    except Exception as e:
        st.error(f"获取模板列表失败: {str(e)}")
        return []

def create_template(template_data: Dict[str, Any]) -> bool:
    """创建模板"""
    try:
        template_service = TemplateService()
        response = template_service.create_template(**template_data)
        return True
    except Exception as e:
        st.error(f"创建模板失败: {str(e)}")
        return False

def update_template(template_id: str, template_data: Dict[str, Any]) -> bool:
    """更新模板"""
    try:
        template_service = TemplateService()
        response = template_service.update_template(template_id, **template_data)
        return True
    except Exception as e:
        st.error(f"更新模板失败: {str(e)}")
        return False

def delete_template(template_id: str) -> bool:
    """删除模板"""
    try:
        template_service = TemplateService()
        if template_service.delete_template(template_id):
            st.success("模板删除成功")
            return True
    except Exception as e:
        st.error(f"删除模板失败: {str(e)}")
        return False

def use_template(template: Dict[str, Any]):
    """使用模板"""
    # 检查是否有变量需要填充
    variables = template.get('variables', [])
    
    if variables:
        st.markdown("#### 填充模板变量")
        
        variable_values = {}
        
        # 为每个变量创建输入框
        for var in variables:
            variable_values[var] = st.text_input(
                f"变量 {{{var}}}",
                key=f"use_var_{var}_{template['id']}",
                placeholder=f"请输入{var}的值"
            )
        
        if st.button("应用模板", key=f"apply_{template['id']}"):
            if all(variable_values.values()):
                # 替换变量
                final_prompt = template['template']
                for var, value in variable_values.items():
                    final_prompt = final_prompt.replace(f"{{{var}}}", value)
                
                # 保存到会话状态
                st.session_state.template_prompt = final_prompt
                st.success("模板已应用，可前往检测页面使用")
                
                if st.button("前往检测页面"):
                    st.switch_page("pages/3_🔍_Detection.py")
            else:
                st.warning("请填写所有变量")
    else:
        # 直接使用模板
        st.session_state.template_prompt = template['template']
        st.success("模板已应用，可前往检测页面使用")
        
        if st.button("前往检测页面"):
            st.switch_page("pages/3_🔍_Detection.py")

def copy_template(template: Dict[str, Any]):
    """复制模板"""
    # 创建副本
    copied_template = {
        **template,
        "name": f"{template['name']} (副本)",
        "id": None  # 新模板需要新ID
    }
    
    if create_template(copied_template):
        st.success("模板复制成功")
        st.rerun()

if __name__ == "__main__":
    main()
