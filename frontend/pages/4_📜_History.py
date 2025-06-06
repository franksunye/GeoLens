"""
检测历史页面
查看和管理历史检测记录
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from components.auth import require_auth
from components.sidebar import render_sidebar
from components.charts import render_detection_results_chart, render_time_series_chart
from services.detection_service import DetectionService
from utils.session import get_current_project

# 页面配置
st.set_page_config(
    page_title="检测历史 - GeoLens",
    page_icon="📜",
    layout="wide"
)

@require_auth
def main():
    """主函数"""
    render_sidebar()
    
    st.markdown("# 📜 检测历史")
    st.markdown("查看和分析历史检测记录")
    
    # 主要功能选项卡
    tab1, tab2, tab3 = st.tabs(["📋 历史记录", "📊 统计分析", "📤 导出数据"])
    
    with tab1:
        render_history_list()
    
    with tab2:
        render_history_analytics()
    
    with tab3:
        render_export_section()

def render_history_list():
    """渲染历史记录列表"""
    st.markdown("### 📋 检测历史记录")
    
    # 筛选控件
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # 项目筛选
        current_project = get_current_project()
        if current_project:
            st.info(f"📁 当前项目: {current_project['name']}")
            project_filter = current_project['id']
        else:
            project_filter = st.selectbox("📁 选择项目", ["全部项目", "项目A", "项目B"])
    
    with col2:
        # 时间范围筛选
        time_range = st.selectbox(
            "📅 时间范围",
            ["最近7天", "最近30天", "最近90天", "自定义"]
        )
    
    with col3:
        # 状态筛选
        status_filter = st.selectbox(
            "📊 检测状态",
            ["全部", "已完成", "进行中", "失败"]
        )
    
    with col4:
        # 排序方式
        sort_by = st.selectbox(
            "📈 排序方式",
            ["创建时间", "提及率", "置信度", "品牌数量"]
        )
    
    # 自定义时间范围
    if time_range == "自定义":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("开始日期", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("结束日期", value=datetime.now())
    
    # 获取历史记录
    history_records = get_history_records(project_filter, time_range, status_filter)
    
    if not history_records:
        st.info("📝 暂无历史记录")
        if st.button("🚀 开始第一次检测"):
            st.switch_page("pages/3_🔍_Detection.py")
        return
    
    # 显示记录统计
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总记录数", len(history_records))
    
    with col2:
        completed_count = len([r for r in history_records if r.get('status') == 'completed'])
        st.metric("已完成", completed_count)
    
    with col3:
        avg_mention_rate = sum(r.get('mention_rate', 0) for r in history_records) / len(history_records)
        st.metric("平均提及率", f"{avg_mention_rate:.1f}%")
    
    with col4:
        total_brands = sum(len(r.get('brands_checked', [])) for r in history_records)
        st.metric("检测品牌总数", total_brands)
    
    # 记录列表
    st.markdown("---")
    
    # 批量操作
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("#### 📋 检测记录")
    
    with col2:
        if st.button("🔄 刷新数据"):
            st.rerun()
    
    with col3:
        if st.button("🗑️ 清理旧记录"):
            show_cleanup_dialog()
    
    # 记录表格
    df = pd.DataFrame(history_records)
    
    if not df.empty:
        # 格式化数据
        df['创建时间'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        df['Prompt'] = df['prompt'].str[:50] + '...'
        df['品牌'] = df['brands_checked'].apply(lambda x: ', '.join(x[:3]) + ('...' if len(x) > 3 else ''))
        df['模型'] = df['models_used'].apply(lambda x: ', '.join(x))
        df['提及率'] = df['mention_rate'].apply(lambda x: f"{x:.1f}%")
        df['状态'] = df['status'].map({
            'completed': '✅ 已完成',
            'running': '🔄 进行中',
            'failed': '❌ 失败',
            'pending': '⏳ 等待中'
        })
        
        # 选择显示列
        display_df = df[['创建时间', 'Prompt', '品牌', '模型', '提及率', '状态']].copy()
        
        # 可选择的记录
        selected_indices = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row"
        )
        
        # 详情查看
        if selected_indices and len(selected_indices['selection']['rows']) > 0:
            selected_idx = selected_indices['selection']['rows'][0]
            selected_record = history_records[selected_idx]
            
            st.markdown("---")
            render_record_detail(selected_record)

def render_record_detail(record: Dict[str, Any]):
    """渲染记录详情"""
    st.markdown("### 🔍 检测详情")
    
    # 基本信息
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 基本信息")
        st.markdown(f"**检测ID**: {record.get('id', 'N/A')}")
        st.markdown(f"**创建时间**: {record.get('created_at', 'N/A')}")
        st.markdown(f"**状态**: {record.get('status', 'N/A')}")
        st.markdown(f"**总提及次数**: {record.get('total_mentions', 0)}")
        st.markdown(f"**平均置信度**: {record.get('avg_confidence', 0):.2f}")
    
    with col2:
        st.markdown("#### 🎯 检测配置")
        st.markdown(f"**检测品牌**: {', '.join(record.get('brands_checked', []))}")
        st.markdown(f"**使用模型**: {', '.join(record.get('models_used', []))}")
        st.markdown(f"**提及率**: {record.get('mention_rate', 0):.1f}%")
    
    # Prompt内容
    st.markdown("#### 📝 检测Prompt")
    st.text_area("", value=record.get('prompt', ''), height=100, disabled=True)
    
    # 检测结果可视化
    if record.get('brand_mentions'):
        st.markdown("#### 📊 检测结果可视化")
        render_detection_results_chart(record['brand_mentions'])
    
    # 操作按钮
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 重新检测", key=f"rerun_{record.get('id')}"):
            # 跳转到检测页面并预填数据
            st.session_state.template_prompt = record.get('prompt', '')
            st.session_state.selected_brands = record.get('brands_checked', [])
            st.session_state.selected_models = record.get('models_used', [])
            st.switch_page("pages/3_🔍_Detection.py")
    
    with col2:
        if st.button("📤 导出结果", key=f"export_{record.get('id')}"):
            export_single_record(record)
    
    with col3:
        if st.button("📋 复制配置", key=f"copy_{record.get('id')}"):
            copy_detection_config(record)
    
    with col4:
        if st.button("🗑️ 删除记录", key=f"delete_{record.get('id')}"):
            delete_record(record.get('id'))

def render_history_analytics():
    """渲染历史分析"""
    st.markdown("### 📊 检测历史分析")
    
    # 获取分析数据
    analytics_data = get_analytics_data()
    
    if not analytics_data:
        st.info("📊 暂无足够数据进行分析")
        return
    
    # 时间趋势分析
    st.markdown("#### 📈 检测趋势分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 检测频率趋势
        if analytics_data.get('detection_frequency'):
            render_time_series_chart(
                analytics_data['detection_frequency'],
                metric='count'
            )
    
    with col2:
        # 提及率趋势
        if analytics_data.get('mention_rate_trend'):
            render_time_series_chart(
                analytics_data['mention_rate_trend'],
                metric='mention_rate'
            )
    
    # 品牌表现分析
    st.markdown("#### 🏷️ 品牌表现分析")
    
    if analytics_data.get('brand_performance'):
        brand_df = pd.DataFrame(analytics_data['brand_performance'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**品牌提及统计**")
            st.dataframe(brand_df, use_container_width=True, hide_index=True)
        
        with col2:
            # 品牌提及率图表
            if not brand_df.empty:
                import plotly.express as px
                fig = px.bar(
                    brand_df,
                    x='brand',
                    y='mention_rate',
                    title='品牌平均提及率',
                    labels={'mention_rate': '提及率 (%)', 'brand': '品牌'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # 模型表现对比
    st.markdown("#### 🤖 AI模型表现对比")
    
    if analytics_data.get('model_performance'):
        model_df = pd.DataFrame(analytics_data['model_performance'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**模型统计**")
            st.dataframe(model_df, use_container_width=True, hide_index=True)
        
        with col2:
            # 模型响应时间对比
            if not model_df.empty:
                import plotly.express as px
                fig = px.bar(
                    model_df,
                    x='model',
                    y='avg_response_time',
                    title='模型平均响应时间',
                    labels={'avg_response_time': '响应时间 (ms)', 'model': '模型'}
                )
                st.plotly_chart(fig, use_container_width=True)

def render_export_section():
    """渲染导出部分"""
    st.markdown("### 📤 数据导出")
    
    # 导出选项
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 导出范围")
        
        export_range = st.radio(
            "选择导出范围",
            ["当前项目", "全部项目", "自定义选择"]
        )
        
        if export_range == "自定义选择":
            # 项目选择
            available_projects = get_available_projects()
            selected_projects = st.multiselect(
                "选择项目",
                options=[p['name'] for p in available_projects]
            )
        
        # 时间范围
        export_time_range = st.selectbox(
            "时间范围",
            ["最近7天", "最近30天", "最近90天", "全部时间", "自定义"]
        )
        
        if export_time_range == "自定义":
            col_start, col_end = st.columns(2)
            with col_start:
                export_start_date = st.date_input("开始日期")
            with col_end:
                export_end_date = st.date_input("结束日期")
    
    with col2:
        st.markdown("#### ⚙️ 导出设置")
        
        export_format = st.selectbox(
            "导出格式",
            ["CSV", "Excel", "JSON"]
        )
        
        include_details = st.checkbox("包含详细结果", value=True)
        include_raw_responses = st.checkbox("包含原始AI回答", value=False)
        
        # 字段选择
        available_fields = [
            "检测时间", "Prompt", "品牌列表", "AI模型",
            "提及次数", "提及率", "平均置信度", "检测状态"
        ]
        
        selected_fields = st.multiselect(
            "选择导出字段",
            options=available_fields,
            default=available_fields[:6]
        )
    
    # 导出预览
    st.markdown("#### 👀 导出预览")
    
    preview_data = get_export_preview(export_range, export_time_range)
    
    if preview_data:
        st.markdown(f"**预计导出记录数**: {len(preview_data)}")
        
        # 显示前几条记录
        preview_df = pd.DataFrame(preview_data[:5])
        st.dataframe(preview_df, use_container_width=True, hide_index=True)
        
        if len(preview_data) > 5:
            st.info(f"... 还有 {len(preview_data) - 5} 条记录")
    else:
        st.info("📝 没有符合条件的记录")
    
    # 导出按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📤 开始导出", type="primary", disabled=not preview_data):
            export_data(
                data=preview_data,
                format=export_format,
                fields=selected_fields,
                include_details=include_details
            )

# 辅助函数
def get_history_records(project_filter: str, time_range: str, status_filter: str) -> List[Dict[str, Any]]:
    """获取历史记录"""
    try:
        detection_service = DetectionService()
        
        # 构建查询参数
        params = {}
        if project_filter and project_filter != "全部项目":
            params['project_id'] = project_filter
        
        if status_filter != "全部":
            status_map = {
                "已完成": "completed",
                "进行中": "running", 
                "失败": "failed"
            }
            params['status'] = status_map.get(status_filter)
        
        response = detection_service.get_detection_history(**params)
        return response.get("data", {}).get("items", [])
        
    except Exception as e:
        st.error(f"获取历史记录失败: {str(e)}")
        return []

def get_analytics_data() -> Dict[str, Any]:
    """获取分析数据"""
    # 模拟分析数据
    return {
        "detection_frequency": [
            {"date": "2024-12-15", "count": 5},
            {"date": "2024-12-16", "count": 8},
            {"date": "2024-12-17", "count": 12},
            {"date": "2024-12-18", "count": 6},
            {"date": "2024-12-19", "count": 10}
        ],
        "mention_rate_trend": [
            {"date": "2024-12-15", "mention_rate": 23.5},
            {"date": "2024-12-16", "mention_rate": 28.2},
            {"date": "2024-12-17", "mention_rate": 31.8},
            {"date": "2024-12-18", "mention_rate": 25.6},
            {"date": "2024-12-19", "mention_rate": 29.4}
        ],
        "brand_performance": [
            {"brand": "Notion", "mention_count": 15, "mention_rate": 45.2},
            {"brand": "Obsidian", "mention_count": 12, "mention_rate": 38.7},
            {"brand": "Roam Research", "mention_count": 8, "mention_rate": 25.8}
        ],
        "model_performance": [
            {"model": "doubao", "usage_count": 25, "avg_response_time": 3500},
            {"model": "deepseek", "usage_count": 23, "avg_response_time": 8200},
            {"model": "openai", "usage_count": 18, "avg_response_time": 2800}
        ]
    }

def get_available_projects() -> List[Dict[str, Any]]:
    """获取可用项目列表"""
    # 模拟项目数据
    return [
        {"id": "1", "name": "SaaS工具监测"},
        {"id": "2", "name": "设计工具分析"}
    ]

def get_export_preview(export_range: str, time_range: str) -> List[Dict[str, Any]]:
    """获取导出预览数据"""
    # 模拟预览数据
    return [
        {
            "检测时间": "2024-12-19 14:30",
            "Prompt": "推荐几个好用的笔记软件",
            "品牌列表": "Notion, Obsidian",
            "AI模型": "doubao, deepseek",
            "提及次数": 3,
            "提及率": "75.0%",
            "平均置信度": 0.85,
            "检测状态": "已完成"
        }
    ]

def export_data(data: List[Dict[str, Any]], format: str, fields: List[str], include_details: bool):
    """导出数据"""
    try:
        if format == "CSV":
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📥 下载CSV文件",
                data=csv,
                file_name=f"geolens_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        elif format == "Excel":
            df = pd.DataFrame(data)
            # 这里需要实现Excel导出逻辑
            st.info("Excel导出功能开发中...")
        
        elif format == "JSON":
            import json
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            st.download_button(
                label="📥 下载JSON文件",
                data=json_data,
                file_name=f"geolens_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.success("✅ 导出完成！")
        
    except Exception as e:
        st.error(f"导出失败: {str(e)}")

def export_single_record(record: Dict[str, Any]):
    """导出单条记录"""
    st.info("📤 单条记录导出功能开发中...")

def copy_detection_config(record: Dict[str, Any]):
    """复制检测配置"""
    st.session_state.template_prompt = record.get('prompt', '')
    st.session_state.selected_brands = record.get('brands_checked', [])
    st.session_state.selected_models = record.get('models_used', [])
    st.success("✅ 配置已复制，可前往检测页面使用")

def delete_record(record_id: str):
    """删除记录"""
    try:
        detection_service = DetectionService()
        if detection_service.delete_detection_record(record_id):
            st.success("✅ 记录删除成功")
            st.rerun()
    except Exception as e:
        st.error(f"删除失败: {str(e)}")

def show_cleanup_dialog():
    """显示清理对话框"""
    st.info("🗑️ 清理功能开发中...")

if __name__ == "__main__":
    main()
