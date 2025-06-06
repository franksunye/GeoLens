"""
引用检测页面
核心功能 - AI引用检测
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

from components.auth import require_auth
from components.sidebar import render_sidebar
from services.api_client import APIClient
from services.detection_service import DetectionService
from components.charts import render_detection_results_chart, render_model_comparison_chart
from utils.session import get_current_project, set_detection_state, get_detection_state

# 页面配置
st.set_page_config(
    page_title="引用检测 - GeoLens",
    page_icon="🔍",
    layout="wide"
)

@require_auth
def main():
    """主函数"""
    render_sidebar()
    
    st.markdown("# 🔍 AI引用检测")
    st.markdown("输入Prompt，选择品牌和AI模型，开始智能引用检测分析")
    
    # 检查当前项目
    current_project = get_current_project()
    if not current_project:
        st.warning("⚠️ 请先选择一个项目")
        if st.button("📁 前往项目管理"):
            st.switch_page("pages/2_📁_Projects.py")
        return
    
    # 显示当前项目信息
    with st.container():
        st.info(f"📁 当前项目: **{current_project.get('name', '未命名项目')}** | 🌐 {current_project.get('domain', '')}")
    
    # 主要内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_detection_form()
    
    with col2:
        render_detection_status()
        render_quick_templates()
    
    # 检测结果展示
    render_detection_results()

def render_detection_form():
    """渲染检测表单"""
    st.markdown("### 📝 检测配置")
    
    with st.form("detection_form"):
        # Prompt输入
        prompt = st.text_area(
            "🎯 检测Prompt",
            height=120,
            placeholder="例如: 推荐几个好用的团队协作和笔记管理工具",
            help="输入您想要检测的问题或场景"
        )
        
        # 品牌选择
        col1, col2 = st.columns(2)
        
        with col1:
            # 从当前项目获取品牌列表
            current_project = get_current_project()
            available_brands = current_project.get('brands', [
                "Notion", "Obsidian", "Roam Research", 
                "Slack", "Teams", "Discord",
                "Figma", "Sketch", "Adobe XD"
            ])
            
            selected_brands = st.multiselect(
                "🏷️ 选择品牌",
                options=available_brands,
                default=st.session_state.get('selected_brands', []),
                help="选择要检测的品牌"
            )
        
        with col2:
            # AI模型选择
            available_models = ["doubao", "deepseek", "openai"]
            selected_models = st.multiselect(
                "🤖 选择AI模型",
                options=available_models,
                default=st.session_state.get('selected_models', ["doubao", "deepseek"]),
                help="选择用于检测的AI模型"
            )
        
        # 高级配置
        with st.expander("⚙️ 高级配置", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                max_tokens = st.number_input(
                    "最大Token数",
                    min_value=100,
                    max_value=1000,
                    value=300,
                    step=50
                )
            
            with col2:
                temperature = st.slider(
                    "温度参数",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.3,
                    step=0.1
                )
            
            with col3:
                parallel_execution = st.checkbox(
                    "并行执行",
                    value=True,
                    help="同时调用多个AI模型"
                )
        
        # 提交按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button(
                "🚀 开始检测",
                type="primary",
                use_container_width=True
            )
    
    # 处理表单提交
    if submit_button:
        if not prompt.strip():
            st.error("❌ 请输入检测Prompt")
            return
        
        if not selected_brands:
            st.error("❌ 请选择至少一个品牌")
            return
        
        if not selected_models:
            st.error("❌ 请选择至少一个AI模型")
            return
        
        # 更新会话状态
        st.session_state.selected_brands = selected_brands
        st.session_state.selected_models = selected_models
        
        # 执行检测
        run_detection(
            prompt=prompt,
            brands=selected_brands,
            models=selected_models,
            max_tokens=max_tokens,
            temperature=temperature,
            parallel_execution=parallel_execution
        )

def run_detection(prompt: str, brands: List[str], models: List[str], 
                 max_tokens: int, temperature: float, parallel_execution: bool):
    """执行检测"""
    
    # 设置检测状态
    set_detection_state(running=True)
    
    # 显示进度
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 准备检测参数
        current_project = get_current_project()
        detection_params = {
            "project_id": current_project.get('id', 'demo-project'),
            "prompt": prompt,
            "brands": brands,
            "models": models,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "parallel_execution": parallel_execution
        }
        
        # 模拟检测过程
        status_text.text("🔄 正在初始化检测...")
        progress_bar.progress(10)
        
        # 调用检测服务
        detection_service = DetectionService()
        
        status_text.text("🤖 正在调用AI模型...")
        progress_bar.progress(30)
        
        # 模拟API调用
        import time
        time.sleep(2)  # 模拟网络延迟
        
        status_text.text("🔍 正在分析检测结果...")
        progress_bar.progress(70)
        
        # 生成模拟结果
        results = generate_mock_detection_results(prompt, brands, models)
        
        status_text.text("✅ 检测完成！")
        progress_bar.progress(100)
        
        # 保存结果
        set_detection_state(running=False, result=results)
        
        st.success("🎉 检测完成！请查看下方结果")
        
    except Exception as e:
        st.error(f"❌ 检测过程中发生错误: {str(e)}")
        set_detection_state(running=False)
    
    finally:
        # 清理进度显示
        progress_bar.empty()
        status_text.empty()

def generate_mock_detection_results(prompt: str, brands: List[str], models: List[str]) -> Dict[str, Any]:
    """生成模拟检测结果"""
    import random
    
    results = {
        "check_id": f"check_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "prompt": prompt,
        "brands_checked": brands,
        "models_used": models,
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "total_mentions": 0,
        "mention_rate": 0.0,
        "avg_confidence": 0.0,
        "model_results": [],
        "brand_mentions": []
    }
    
    # 为每个模型生成结果
    for model in models:
        model_result = {
            "model": model,
            "response_text": f"基于{model}模型的回答: 这里是关于{prompt}的详细回答...",
            "processing_time_ms": random.randint(2000, 8000),
            "mentions": []
        }
        
        # 为每个品牌生成提及结果
        for brand in brands:
            mentioned = random.choice([True, False, False])  # 33%概率被提及
            if mentioned:
                mention = {
                    "brand": brand,
                    "mentioned": True,
                    "confidence_score": round(random.uniform(0.7, 0.95), 2),
                    "context_snippet": f"...推荐使用{brand}，它是一个优秀的工具...",
                    "position": random.randint(50, 200)
                }
                model_result["mentions"].append(mention)
                results["brand_mentions"].append(mention)
        
        results["model_results"].append(model_result)
    
    # 计算总体统计
    total_mentions = len(results["brand_mentions"])
    results["total_mentions"] = total_mentions
    results["mention_rate"] = round(total_mentions / (len(brands) * len(models)) * 100, 1)
    
    if results["brand_mentions"]:
        avg_confidence = sum(m["confidence_score"] for m in results["brand_mentions"]) / len(results["brand_mentions"])
        results["avg_confidence"] = round(avg_confidence, 2)
    
    return results

def render_detection_status():
    """渲染检测状态"""
    st.markdown("### 📊 检测状态")
    
    running, last_result = get_detection_state()
    
    if running:
        st.info("🔄 检测进行中...")
    elif last_result:
        st.success("✅ 最近检测完成")
        
        # 显示简要统计
        col1, col2 = st.columns(2)
        with col1:
            st.metric("提及次数", last_result.get("total_mentions", 0))
        with col2:
            st.metric("提及率", f"{last_result.get('mention_rate', 0)}%")
        
        if st.button("📊 查看详细结果"):
            st.rerun()
    else:
        st.info("💡 尚未进行检测")

def render_quick_templates():
    """渲染快速模板"""
    st.markdown("### 📚 快速模板")
    
    templates = [
        {
            "name": "笔记软件推荐",
            "prompt": "推荐几个好用的笔记管理软件",
            "brands": ["Notion", "Obsidian", "Roam Research"]
        },
        {
            "name": "团队协作工具",
            "prompt": "比较主流的团队协作工具",
            "brands": ["Slack", "Teams", "Discord"]
        },
        {
            "name": "设计工具对比",
            "prompt": "介绍几个专业的UI设计工具",
            "brands": ["Figma", "Sketch", "Adobe XD"]
        }
    ]
    
    for template in templates:
        if st.button(
            template["name"],
            key=f"template_{template['name']}",
            help=f"Prompt: {template['prompt']}"
        ):
            # 应用模板到表单
            st.session_state.template_prompt = template["prompt"]
            st.session_state.selected_brands = template["brands"]
            st.rerun()

def render_detection_results():
    """渲染检测结果"""
    running, last_result = get_detection_state()
    
    if not last_result:
        return
    
    st.markdown("---")
    st.markdown("## 📊 检测结果")
    
    # 结果概览
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "总提及次数",
            last_result.get("total_mentions", 0),
            help="所有模型中品牌被提及的总次数"
        )
    
    with col2:
        st.metric(
            "平均提及率",
            f"{last_result.get('mention_rate', 0)}%",
            help="品牌被提及的平均概率"
        )
    
    with col3:
        st.metric(
            "平均置信度",
            f"{last_result.get('avg_confidence', 0):.2f}",
            help="检测结果的平均置信度"
        )
    
    with col4:
        st.metric(
            "检测模型数",
            len(last_result.get("models_used", [])),
            help="参与检测的AI模型数量"
        )
    
    # 详细结果展示
    tab1, tab2, tab3 = st.tabs(["📊 可视化结果", "📝 详细数据", "🤖 模型回答"])
    
    with tab1:
        render_results_visualization(last_result)
    
    with tab2:
        render_results_table(last_result)
    
    with tab3:
        render_model_responses(last_result)

def render_results_visualization(results: Dict[str, Any]):
    """渲染结果可视化"""
    
    # 品牌提及率图表
    if results.get("brand_mentions"):
        render_detection_results_chart(results["brand_mentions"])
    
    # 模型性能对比
    if results.get("model_results"):
        render_model_comparison_chart(results["model_results"])

def render_results_table(results: Dict[str, Any]):
    """渲染结果表格"""
    import pandas as pd
    
    if results.get("brand_mentions"):
        df = pd.DataFrame(results["brand_mentions"])
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📝 暂无品牌提及数据")

def render_model_responses(results: Dict[str, Any]):
    """渲染模型回答"""
    for model_result in results.get("model_results", []):
        with st.expander(f"🤖 {model_result['model'].title()} 模型回答", expanded=False):
            st.markdown(f"**处理时间**: {model_result['processing_time_ms']}ms")
            st.markdown("**回答内容**:")
            st.text_area(
                "",
                value=model_result["response_text"],
                height=150,
                disabled=True,
                key=f"response_{model_result['model']}"
            )
            
            if model_result.get("mentions"):
                st.markdown("**检测到的品牌提及**:")
                for mention in model_result["mentions"]:
                    st.markdown(f"- **{mention['brand']}** (置信度: {mention['confidence_score']:.2f})")
                    st.markdown(f"  > {mention['context_snippet']}")

if __name__ == "__main__":
    main()
