from styles.enterprise_theme import apply_enterprise_theme, render_enterprise_header, render_status_badge
"""
数据分析页面
品牌提及分析和可视化
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Any

from components.auth import require_auth
from components.sidebar import render_sidebar
from components.charts import (
    render_brand_trend_chart, render_confidence_radar_chart,
    render_comparison_heatmap, render_metrics_dashboard
)
from services.detection_service import DetectionService
from utils.session import get_current_project

# 页面配置
st.set_page_config(
    page_title="数据分析 - GeoLens",
    page_icon="📊",
    layout="wide"
)

# 应用企业级主题
apply_enterprise_theme()

@require_auth
def main():
    """主函数"""
    render_sidebar()
    
    render_enterprise_header("数据分析", "")
    st.markdown("深入分析品牌在AI中的表现和趋势")
    
    # 检查当前项目
    current_project = get_current_project()
    if not current_project:
        st.warning("请先选择一个项目")
        if st.button("前往项目管理"):
            st.switch_page("pages/2_📁_Projects.py")
        return
    
    # 显示当前项目信息
    st.info(f"当前项目: **{current_project.get('name', '未命名项目')}**")
    
    # 主要功能选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["趋势分析", "品牌对比", "模型分析", "综合报告"])
    
    with tab1:
        render_trend_analysis()
    
    with tab2:
        render_brand_comparison()
    
    with tab3:
        render_model_analysis()
    
    with tab4:
        render_comprehensive_report()

def render_trend_analysis():
    """渲染趋势分析"""
    st.markdown("### 品牌提及趋势分析")
    
    # 分析配置
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_range = st.selectbox(
            "时间范围",
            ["最近7天", "最近30天", "最近90天", "自定义"]
        )
    
    with col2:
        current_project = get_current_project()
        available_brands = current_project.get('brands', [])
        selected_brands = st.multiselect(
            "选择品牌",
            options=available_brands,
            default=available_brands[:3] if len(available_brands) >= 3 else available_brands
        )
    
    with col3:
        metric_type = st.selectbox(
            "分析指标",
            ["提及率", "置信度", "检测次数"]
        )
    
    if not selected_brands:
        st.warning("请选择至少一个品牌进行分析")
        return
    
    # 获取趋势数据
    trend_data = get_trend_data(selected_brands, time_range, metric_type)
    
    if not trend_data:
        st.info("暂无趋势数据")
        return
    
    # 趋势图表
    render_brand_trend_chart(trend_data, selected_brands)
    
    # 趋势统计
    st.markdown("#### 趋势统计")
    
    trend_stats = calculate_trend_stats(trend_data, selected_brands)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "平均提及率",
            f"{trend_stats.get('avg_mention_rate', 0):.1f}%",
            delta=f"{trend_stats.get('mention_rate_change', 0):.1f}%"
        )
    
    with col2:
        st.metric(
            "最高提及率",
            f"{trend_stats.get('max_mention_rate', 0):.1f}%",
            delta=trend_stats.get('best_brand', 'N/A')
        )
    
    with col3:
        st.metric(
            "平均置信度",
            f"{trend_stats.get('avg_confidence', 0):.2f}",
            delta=f"{trend_stats.get('confidence_change', 0):.2f}"
        )
    
    with col4:
        st.metric(
            "检测总次数",
            trend_stats.get('total_detections', 0),
            delta=f"{trend_stats.get('detection_change', 0)}"
        )

def render_brand_comparison():
    """渲染品牌对比分析"""
    st.markdown("### 品牌对比分析")
    
    # 对比配置
    col1, col2 = st.columns(2)
    
    with col1:
        current_project = get_current_project()
        available_brands = current_project.get('brands', [])
        comparison_brands = st.multiselect(
            "选择对比品牌",
            options=available_brands,
            default=available_brands[:4] if len(available_brands) >= 4 else available_brands,
            help="选择2-6个品牌进行对比分析"
        )
    
    with col2:
        comparison_metrics = st.multiselect(
            "对比指标",
            options=["提及率", "置信度", "响应时间", "检测频次"],
            default=["提及率", "置信度"]
        )
    
    if len(comparison_brands) < 2:
        st.warning("请选择至少2个品牌进行对比")
        return
    
    # 获取对比数据
    comparison_data = get_comparison_data(comparison_brands, comparison_metrics)
    
    if not comparison_data:
        st.info("暂无对比数据")
        return
    
    # 对比图表
    col1, col2 = st.columns(2)
    
    with col1:
        # 品牌提及率对比
        if "提及率" in comparison_metrics:
            render_mention_rate_comparison(comparison_data)
    
    with col2:
        # 置信度雷达图
        if "置信度" in comparison_metrics:
            render_confidence_radar_chart(comparison_data.get('confidence_data', []))
    
    # 详细对比表格
    st.markdown("#### 详细对比数据")
    
    comparison_df = pd.DataFrame(comparison_data.get('summary_data', []))
    
    if not comparison_df.empty:
        # 格式化数据
        if '提及率' in comparison_df.columns:
            comparison_df['提及率'] = comparison_df['提及率'].apply(lambda x: f"{x:.1f}%")
        if '置信度' in comparison_df.columns:
            comparison_df['置信度'] = comparison_df['置信度'].apply(lambda x: f"{x:.2f}")
        
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # 竞品分析洞察
    st.markdown("#### 竞品分析洞察")
    
    insights = generate_brand_insights(comparison_data, comparison_brands)
    
    for insight in insights:
        st.markdown(f"- {insight}")

def render_model_analysis():
    """渲染模型分析"""
    st.markdown("### AI模型性能分析")
    
    # 模型配置
    col1, col2 = st.columns(2)
    
    with col1:
        available_models = ["doubao", "deepseek", "openai"]
        selected_models = st.multiselect(
            "选择模型",
            options=available_models,
            default=available_models
        )
    
    with col2:
        analysis_dimension = st.selectbox(
            "分析维度",
            ["响应时间", "检测准确率", "品牌覆盖率", "综合表现"]
        )
    
    if not selected_models:
        st.warning("请选择至少一个模型进行分析")
        return
    
    # 获取模型数据
    model_data = get_model_analysis_data(selected_models, analysis_dimension)
    
    if not model_data:
        st.info("暂无模型分析数据")
        return
    
    # 模型性能图表
    col1, col2 = st.columns(2)
    
    with col1:
        # 响应时间对比
        render_model_response_time_chart(model_data)
    
    with col2:
        # 检测准确率对比
        render_model_accuracy_chart(model_data)
    
    # 模型详细统计
    st.markdown("#### 模型详细统计")
    
    model_stats_df = pd.DataFrame(model_data.get('model_stats', []))
    
    if not model_stats_df.empty:
        st.dataframe(model_stats_df, use_container_width=True, hide_index=True)
    
    # 模型推荐
    st.markdown("#### 模型使用建议")
    
    recommendations = generate_model_recommendations(model_data, selected_models)
    
    for rec in recommendations:
        st.markdown(f"- {rec}")

def render_comprehensive_report():
    """渲染综合报告"""
    st.markdown("### 综合分析报告")
    
    # 报告配置
    col1, col2 = st.columns(2)
    
    with col1:
        report_period = st.selectbox(
            "报告周期",
            ["本周", "本月", "本季度", "自定义"]
        )
    
    with col2:
        report_format = st.selectbox(
            "报告格式",
            ["在线查看", "PDF导出", "Excel导出"]
        )
    
    # 生成综合报告
    report_data = generate_comprehensive_report(report_period)
    
    if not report_data:
        st.info("暂无报告数据")
        return
    
    # 关键指标概览
    render_metrics_dashboard(report_data.get('key_metrics', {}))
    
    # 报告内容
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 主要发现")
        
        findings = report_data.get('key_findings', [])
        for finding in findings:
            st.markdown(f"- {finding}")
    
    with col2:
        st.markdown("#### 行动建议")
        
        recommendations = report_data.get('recommendations', [])
        for rec in recommendations:
            st.markdown(f"- {rec}")
    
    # 详细分析
    st.markdown("#### 详细分析")
    
    # 品牌表现排名
    if report_data.get('brand_ranking'):
        st.markdown("**品牌表现排名**")
        ranking_df = pd.DataFrame(report_data['brand_ranking'])
        st.dataframe(ranking_df, use_container_width=True, hide_index=True)
    
    # 趋势变化
    if report_data.get('trend_changes'):
        st.markdown("**趋势变化分析**")
        for change in report_data['trend_changes']:
            st.markdown(f"- {change}")
    
    # 导出报告
    if report_format != "在线查看":
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("导出报告", type="primary"):
                export_report(report_data, report_format)

# 辅助函数
def get_trend_data(brands: List[str], time_range: str, metric: str) -> List[Dict[str, Any]]:
    """获取趋势数据"""
    # 模拟趋势数据
    import random
    from datetime import datetime, timedelta
    
    trend_data = []
    
    # 生成日期范围
    if time_range == "最近7天":
        days = 7
    elif time_range == "最近30天":
        days = 30
    else:
        days = 90
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        
        for brand in brands:
            trend_data.append({
                'date': date,
                'brand': brand,
                'mention_rate': random.uniform(15, 45),
                'confidence': random.uniform(0.6, 0.9),
                'detection_count': random.randint(1, 10)
            })
    
    return trend_data

def calculate_trend_stats(trend_data: List[Dict[str, Any]], brands: List[str]) -> Dict[str, Any]:
    """计算趋势统计"""
    if not trend_data:
        return {}
    
    df = pd.DataFrame(trend_data)
    
    return {
        'avg_mention_rate': df['mention_rate'].mean(),
        'max_mention_rate': df['mention_rate'].max(),
        'avg_confidence': df['confidence'].mean(),
        'total_detections': df['detection_count'].sum(),
        'mention_rate_change': 5.2,  # 模拟变化
        'confidence_change': 0.05,
        'detection_change': 12,
        'best_brand': df.loc[df['mention_rate'].idxmax(), 'brand']
    }

def get_comparison_data(brands: List[str], metrics: List[str]) -> Dict[str, Any]:
    """获取对比数据"""
    import random
    
    summary_data = []
    confidence_data = []
    
    for brand in brands:
        brand_data = {
            '品牌': brand,
            '提及率': random.uniform(20, 50),
            '置信度': random.uniform(0.7, 0.95),
            '响应时间': random.randint(2000, 8000),
            '检测频次': random.randint(10, 50)
        }
        summary_data.append(brand_data)
        
        # 为雷达图准备数据
        for model in ["doubao", "deepseek", "openai"]:
            confidence_data.append({
                'brand': brand,
                'model': model,
                'confidence_score': random.uniform(0.6, 0.9)
            })
    
    return {
        'summary_data': summary_data,
        'confidence_data': confidence_data
    }

def render_mention_rate_comparison(comparison_data: Dict[str, Any]):
    """渲染提及率对比图"""
    summary_data = comparison_data.get('summary_data', [])
    
    if not summary_data:
        return
    
    df = pd.DataFrame(summary_data)
    
    fig = px.bar(
        df,
        x='品牌',
        y='提及率',
        title='品牌提及率对比',
        color='提及率',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def get_model_analysis_data(models: List[str], dimension: str) -> Dict[str, Any]:
    """获取模型分析数据"""
    import random
    
    model_stats = []
    
    for model in models:
        stats = {
            '模型': model.title(),
            '平均响应时间(ms)': random.randint(2000, 8000),
            '检测准确率(%)': random.uniform(85, 95),
            '品牌覆盖率(%)': random.uniform(70, 90),
            '使用次数': random.randint(50, 200)
        }
        model_stats.append(stats)
    
    return {
        'model_stats': model_stats,
        'response_times': [s['平均响应时间(ms)'] for s in model_stats],
        'accuracy_rates': [s['检测准确率(%)'] for s in model_stats]
    }

def render_model_response_time_chart(model_data: Dict[str, Any]):
    """渲染模型响应时间图表"""
    model_stats = model_data.get('model_stats', [])
    
    if not model_stats:
        return
    
    df = pd.DataFrame(model_stats)
    
    fig = px.bar(
        df,
        x='模型',
        y='平均响应时间(ms)',
        title='模型响应时间对比',
        color='平均响应时间(ms)',
        color_continuous_scale='RdYlBu_r'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def render_model_accuracy_chart(model_data: Dict[str, Any]):
    """渲染模型准确率图表"""
    model_stats = model_data.get('model_stats', [])
    
    if not model_stats:
        return
    
    df = pd.DataFrame(model_stats)
    
    fig = px.bar(
        df,
        x='模型',
        y='检测准确率(%)',
        title='模型检测准确率对比',
        color='检测准确率(%)',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def generate_brand_insights(comparison_data: Dict[str, Any], brands: List[str]) -> List[str]:
    """生成品牌洞察"""
    insights = [
        f"在{len(brands)}个品牌中，表现最佳的是排名前2位的品牌",
        "品牌提及率与置信度呈正相关关系",
        "建议重点优化表现较弱品牌的AI可见性策略",
        "不同AI模型对品牌的偏好存在差异，建议多模型并行检测"
    ]
    
    return insights

def generate_model_recommendations(model_data: Dict[str, Any], models: List[str]) -> List[str]:
    """生成模型推荐"""
    recommendations = [
        "对于快速检测需求，推荐使用响应时间最短的模型",
        "对于准确性要求高的场景，建议使用准确率最高的模型",
        "建议根据不同使用场景选择合适的模型组合",
        "定期评估模型性能，及时调整检测策略"
    ]
    
    return recommendations

def generate_comprehensive_report(period: str) -> Dict[str, Any]:
    """生成综合报告"""
    return {
        'key_metrics': {
            'total_detections': 156,
            'avg_mention_rate': 28.5,
            'avg_confidence': 0.82,
            'active_brands': 8,
            'detections_delta': 12,
            'mention_rate_delta': 3.2,
            'confidence_delta': 0.05,
            'brands_delta': 2
        },
        'key_findings': [
            "本周期检测活动显著增加，总检测次数较上期增长12次",
            "平均提及率提升3.2%，显示品牌AI可见性持续改善",
            "置信度稳定在0.82以上，检测质量保持高水平",
            "新增2个活跃品牌，监测覆盖面进一步扩大"
        ],
        'recommendations': [
            "继续保持当前检测频率，确保数据的时效性",
            "重点关注提及率较低的品牌，制定针对性优化策略",
            "考虑增加新的AI模型，提高检测的全面性",
            "建立定期报告机制，及时跟踪品牌表现变化"
        ],
        'brand_ranking': [
            {'排名': 1, '品牌': 'Notion', '提及率': '45.2%', '置信度': 0.89},
            {'排名': 2, '品牌': 'Obsidian', '提及率': '38.7%', '置信度': 0.85},
            {'排名': 3, '品牌': 'Roam Research', '提及率': '25.8%', '置信度': 0.78}
        ],
        'trend_changes': [
            "Notion品牌提及率环比上升8.5%，表现突出",
            "整体置信度水平稳定，波动幅度控制在5%以内",
            "新兴品牌开始获得AI模型关注，值得持续跟踪"
        ]
    }

def export_report(report_data: Dict[str, Any], format: str):
    """导出报告"""
    if format == "PDF导出":
        st.info("PDF导出功能开发中...")
    elif format == "Excel导出":
        st.info("Excel导出功能开发中...")

if __name__ == "__main__":
    main()
