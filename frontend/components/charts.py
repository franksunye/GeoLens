"""
图表组件
数据可视化图表组件
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any, Optional
import numpy as np

def render_detection_results_chart(brand_mentions: List[Dict[str, Any]]):
    """渲染检测结果图表"""
    if not brand_mentions:
        st.info("📊 暂无检测数据")
        return
    
    # 转换为DataFrame
    df = pd.DataFrame(brand_mentions)
    
    # 品牌提及率柱状图
    st.markdown("#### 📊 品牌提及率分析")
    
    # 按品牌统计提及次数
    brand_stats = df.groupby('brand').agg({
        'mentioned': 'sum',
        'confidence_score': 'mean'
    }).reset_index()
    
    brand_stats.columns = ['品牌', '提及次数', '平均置信度']
    
    # 创建柱状图
    fig = px.bar(
        brand_stats,
        x='品牌',
        y='提及次数',
        color='平均置信度',
        color_continuous_scale='Viridis',
        title='品牌提及次数和平均置信度',
        labels={'提及次数': '提及次数', '品牌': '品牌名称'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        xaxis_title="品牌",
        yaxis_title="提及次数"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 置信度分布图
    if len(df) > 1:
        st.markdown("#### 🎯 置信度分布")
        
        fig_confidence = px.histogram(
            df,
            x='confidence_score',
            nbins=10,
            title='检测置信度分布',
            labels={'confidence_score': '置信度', 'count': '频次'}
        )
        
        fig_confidence.update_layout(height=300)
        st.plotly_chart(fig_confidence, use_container_width=True)

def render_model_comparison_chart(model_results: List[Dict[str, Any]]):
    """渲染模型对比图表"""
    if not model_results:
        st.info("📊 暂无模型数据")
        return
    
    st.markdown("#### 🤖 AI模型性能对比")
    
    # 准备数据
    model_data = []
    for result in model_results:
        model_data.append({
            '模型': result['model'].title(),
            '处理时间(ms)': result.get('processing_time_ms', 0),
            '检测到品牌数': len(result.get('mentions', [])),
            '平均置信度': np.mean([m['confidence_score'] for m in result.get('mentions', [])]) if result.get('mentions') else 0
        })
    
    df_models = pd.DataFrame(model_data)
    
    # 创建子图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('处理时间对比', '检测效果对比'),
        specs=[[{"secondary_y": False}, {"secondary_y": True}]]
    )
    
    # 处理时间柱状图
    fig.add_trace(
        go.Bar(
            x=df_models['模型'],
            y=df_models['处理时间(ms)'],
            name='处理时间',
            marker_color='lightblue'
        ),
        row=1, col=1
    )
    
    # 检测效果对比
    fig.add_trace(
        go.Bar(
            x=df_models['模型'],
            y=df_models['检测到品牌数'],
            name='检测到品牌数',
            marker_color='lightgreen'
        ),
        row=1, col=2
    )
    
    # 添加置信度线图
    fig.add_trace(
        go.Scatter(
            x=df_models['模型'],
            y=df_models['平均置信度'],
            mode='lines+markers',
            name='平均置信度',
            line=dict(color='red', width=3),
            yaxis='y2'
        ),
        row=1, col=2
    )
    
    # 更新布局
    fig.update_layout(
        height=400,
        showlegend=True,
        title_text="AI模型性能综合对比"
    )
    
    # 更新y轴标签
    fig.update_yaxes(title_text="处理时间 (毫秒)", row=1, col=1)
    fig.update_yaxes(title_text="检测到品牌数", row=1, col=2)
    fig.update_yaxes(title_text="平均置信度", secondary_y=True, row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

def render_brand_trend_chart(trend_data: List[Dict[str, Any]], brands: List[str]):
    """渲染品牌趋势图表"""
    if not trend_data:
        st.info("📈 暂无趋势数据")
        return
    
    st.markdown("#### 📈 品牌提及趋势")
    
    # 转换数据格式
    df_trend = pd.DataFrame(trend_data)
    
    # 创建折线图
    fig = px.line(
        df_trend,
        x='date',
        y='mention_rate',
        color='brand',
        title='品牌提及率趋势变化',
        labels={'mention_rate': '提及率 (%)', 'date': '日期', 'brand': '品牌'}
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="日期",
        yaxis_title="提及率 (%)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_confidence_radar_chart(brand_data: List[Dict[str, Any]]):
    """渲染置信度雷达图"""
    if not brand_data:
        st.info("🎯 暂无置信度数据")
        return
    
    st.markdown("#### 🎯 品牌检测置信度雷达图")
    
    # 准备雷达图数据
    brands = list(set([item['brand'] for item in brand_data]))
    models = list(set([item['model'] for item in brand_data]))
    
    fig = go.Figure()
    
    for brand in brands:
        brand_scores = []
        for model in models:
            # 找到对应的置信度
            score = 0
            for item in brand_data:
                if item['brand'] == brand and item['model'] == model:
                    score = item.get('confidence_score', 0)
                    break
            brand_scores.append(score)
        
        fig.add_trace(go.Scatterpolar(
            r=brand_scores,
            theta=models,
            fill='toself',
            name=brand
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="品牌在不同AI模型中的检测置信度",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_comparison_heatmap(comparison_data: Dict[str, Any]):
    """渲染对比热力图"""
    if not comparison_data:
        st.info("🔥 暂无对比数据")
        return
    
    st.markdown("#### 🔥 品牌-模型提及热力图")
    
    # 准备热力图数据
    brands = comparison_data.get('brands', [])
    models = comparison_data.get('models', [])
    matrix = comparison_data.get('mention_matrix', [])
    
    if not matrix:
        st.info("📊 暂无矩阵数据")
        return
    
    # 创建热力图
    fig = px.imshow(
        matrix,
        x=models,
        y=brands,
        color_continuous_scale='RdYlBu_r',
        title='品牌在不同AI模型中的提及情况',
        labels={'color': '提及率'}
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="AI模型",
        yaxis_title="品牌"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_metrics_dashboard(metrics: Dict[str, Any]):
    """渲染指标仪表板"""
    st.markdown("#### 📊 关键指标概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="总检测次数",
            value=metrics.get('total_detections', 0),
            delta=metrics.get('detections_delta', 0)
        )
    
    with col2:
        st.metric(
            label="平均提及率",
            value=f"{metrics.get('avg_mention_rate', 0):.1f}%",
            delta=f"{metrics.get('mention_rate_delta', 0):.1f}%"
        )
    
    with col3:
        st.metric(
            label="平均置信度",
            value=f"{metrics.get('avg_confidence', 0):.2f}",
            delta=f"{metrics.get('confidence_delta', 0):.2f}"
        )
    
    with col4:
        st.metric(
            label="活跃品牌数",
            value=metrics.get('active_brands', 0),
            delta=metrics.get('brands_delta', 0)
        )

def render_time_series_chart(time_data: List[Dict[str, Any]], metric: str = 'mention_rate'):
    """渲染时间序列图表"""
    if not time_data:
        st.info("📅 暂无时间序列数据")
        return
    
    df = pd.DataFrame(time_data)
    
    # 确保日期格式正确
    df['date'] = pd.to_datetime(df['date'])
    
    # 创建时间序列图
    fig = px.line(
        df,
        x='date',
        y=metric,
        title=f'{metric.replace("_", " ").title()} 时间趋势',
        labels={metric: metric.replace("_", " ").title(), 'date': '日期'}
    )
    
    fig.update_layout(
        height=300,
        xaxis_title="日期",
        yaxis_title=metric.replace("_", " ").title()
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_distribution_chart(data: List[float], title: str, x_label: str):
    """渲染分布图表"""
    if not data:
        st.info(f"📊 暂无{title}数据")
        return
    
    # 创建直方图
    fig = px.histogram(
        x=data,
        nbins=20,
        title=title,
        labels={'x': x_label, 'count': '频次'}
    )
    
    # 添加统计信息
    mean_val = np.mean(data)
    median_val = np.median(data)
    
    fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                  annotation_text=f"平均值: {mean_val:.2f}")
    fig.add_vline(x=median_val, line_dash="dash", line_color="blue", 
                  annotation_text=f"中位数: {median_val:.2f}")
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_pie_chart(data: Dict[str, int], title: str):
    """渲染饼图"""
    if not data:
        st.info(f"🥧 暂无{title}数据")
        return
    
    # 创建饼图
    fig = px.pie(
        values=list(data.values()),
        names=list(data.keys()),
        title=title
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def render_scatter_plot(x_data: List[float], y_data: List[float], 
                       labels: List[str], title: str, x_label: str, y_label: str):
    """渲染散点图"""
    if not x_data or not y_data:
        st.info(f"📍 暂无{title}数据")
        return
    
    # 创建散点图
    fig = px.scatter(
        x=x_data,
        y=y_data,
        text=labels,
        title=title,
        labels={'x': x_label, 'y': y_label}
    )
    
    fig.update_traces(textposition='top center')
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)
