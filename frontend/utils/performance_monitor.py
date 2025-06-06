"""
性能监控工具
监控应用性能和用户体验指标
"""

import streamlit as st
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from dataclasses import dataclass
import json

@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str = "general"
    metadata: Dict[str, Any] = None

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = []
        self.max_metrics = 1000  # 最大保存指标数
        self.thresholds = {
            'page_load_time': 3.0,  # 页面加载时间阈值(秒)
            'api_response_time': 2.0,  # API响应时间阈值(秒)
            'memory_usage': 80.0,  # 内存使用率阈值(%)
            'cpu_usage': 70.0,  # CPU使用率阈值(%)
        }
        
        # 初始化监控存储
        self._init_monitoring_storage()
    
    def _init_monitoring_storage(self):
        """初始化监控存储"""
        if 'performance_metrics' not in st.session_state:
            st.session_state.performance_metrics = []
        
        if 'performance_alerts' not in st.session_state:
            st.session_state.performance_alerts = []
    
    def record_metric(self, name: str, value: float, unit: str = "",
                     category: str = "general", metadata: Optional[Dict] = None):
        """记录性能指标"""
        # 确保初始化
        self._init_monitoring_storage()

        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            category=category,
            metadata=metadata or {}
        )

        # 添加到会话存储
        st.session_state.performance_metrics.append(metric)
        
        # 保持最近的指标
        if len(st.session_state.performance_metrics) > self.max_metrics:
            st.session_state.performance_metrics = st.session_state.performance_metrics[-self.max_metrics:]
        
        # 检查阈值
        self._check_threshold(metric)
    
    def _check_threshold(self, metric: PerformanceMetric):
        """检查性能阈值"""
        threshold_key = metric.name.lower().replace(' ', '_')
        threshold = self.thresholds.get(threshold_key)
        
        if threshold and metric.value > threshold:
            alert = {
                'timestamp': metric.timestamp.isoformat(),
                'metric_name': metric.name,
                'value': metric.value,
                'threshold': threshold,
                'unit': metric.unit,
                'severity': 'warning' if metric.value < threshold * 1.5 else 'critical'
            }
            
            st.session_state.performance_alerts.append(alert)
            
            # 保持最近50条告警
            if len(st.session_state.performance_alerts) > 50:
                st.session_state.performance_alerts = st.session_state.performance_alerts[-50:]
    
    def get_metrics(self, category: Optional[str] = None,
                   since: Optional[datetime] = None) -> List[PerformanceMetric]:
        """获取性能指标"""
        # 确保初始化
        self._init_monitoring_storage()
        metrics = st.session_state.performance_metrics
        
        # 按类别筛选
        if category:
            metrics = [m for m in metrics if m.category == category]
        
        # 按时间筛选
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        
        return metrics
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """获取性能告警"""
        alerts = st.session_state.performance_alerts
        
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        
        return alerts
    
    def get_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        # 确保初始化
        self._init_monitoring_storage()
        metrics = st.session_state.performance_metrics
        alerts = st.session_state.performance_alerts
        
        if not metrics:
            return {
                'total_metrics': 0,
                'total_alerts': 0,
                'avg_page_load_time': 0,
                'avg_api_response_time': 0,
                'memory_usage': 0,
                'cpu_usage': 0
            }
        
        # 计算平均值
        page_load_times = [m.value for m in metrics if m.name == 'Page Load Time']
        api_response_times = [m.value for m in metrics if m.name == 'API Response Time']
        
        # 获取系统资源使用情况
        try:
            memory_usage = psutil.virtual_memory().percent
            cpu_usage = psutil.cpu_percent()
        except:
            memory_usage = 0
            cpu_usage = 0
        
        return {
            'total_metrics': len(metrics),
            'total_alerts': len(alerts),
            'critical_alerts': len([a for a in alerts if a['severity'] == 'critical']),
            'avg_page_load_time': sum(page_load_times) / len(page_load_times) if page_load_times else 0,
            'avg_api_response_time': sum(api_response_times) / len(api_response_times) if api_response_times else 0,
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
            'last_updated': datetime.now().isoformat()
        }
    
    def clear_metrics(self, category: Optional[str] = None):
        """清除性能指标"""
        if category:
            st.session_state.performance_metrics = [
                m for m in st.session_state.performance_metrics 
                if m.category != category
            ]
        else:
            st.session_state.performance_metrics = []
    
    def clear_alerts(self):
        """清除性能告警"""
        st.session_state.performance_alerts = []

# 全局性能监控器实例
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

# 便捷函数
def record_metric(name: str, value: float, unit: str = "", 
                 category: str = "general", metadata: Optional[Dict] = None):
    """记录性能指标"""
    get_performance_monitor().record_metric(name, value, unit, category, metadata)

def get_performance_summary() -> Dict[str, Any]:
    """获取性能摘要"""
    return get_performance_monitor().get_summary()

# 装饰器
def monitor_performance(metric_name: str, category: str = "function", 
                       unit: str = "seconds"):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                record_metric(
                    name=metric_name,
                    value=execution_time,
                    unit=unit,
                    category=category,
                    metadata={
                        'function': func.__name__,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs),
                        'success': True
                    }
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                record_metric(
                    name=f"{metric_name} (Error)",
                    value=execution_time,
                    unit=unit,
                    category=category,
                    metadata={
                        'function': func.__name__,
                        'error': str(e),
                        'success': False
                    }
                )
                
                raise
        
        return wrapper
    return decorator

class PerformanceTimer:
    """性能计时器上下文管理器"""
    
    def __init__(self, metric_name: str, category: str = "timer", unit: str = "seconds"):
        self.metric_name = metric_name
        self.category = category
        self.unit = unit
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time = time.time() - self.start_time
            
            record_metric(
                name=self.metric_name,
                value=execution_time,
                unit=self.unit,
                category=self.category,
                metadata={
                    'success': exc_type is None,
                    'error': str(exc_val) if exc_val else None
                }
            )

def show_performance_dashboard():
    """显示性能监控面板"""
    st.markdown("### 📊 性能监控面板")
    
    monitor = get_performance_monitor()
    summary = monitor.get_summary()
    
    # 性能概览
    st.markdown("#### 📈 性能概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "总指标数",
            summary['total_metrics'],
            help="记录的性能指标总数"
        )
    
    with col2:
        st.metric(
            "告警数",
            summary['total_alerts'],
            delta=f"{summary['critical_alerts']} 严重",
            help="性能告警总数"
        )
    
    with col3:
        avg_load_time = summary['avg_page_load_time']
        load_time_status = "正常" if avg_load_time < 3.0 else "偏慢"
        st.metric(
            "平均加载时间",
            f"{avg_load_time:.2f}s",
            delta=load_time_status,
            help="页面平均加载时间"
        )
    
    with col4:
        memory_usage = summary['memory_usage']
        memory_status = "正常" if memory_usage < 80 else "偏高"
        st.metric(
            "内存使用率",
            f"{memory_usage:.1f}%",
            delta=memory_status,
            help="系统内存使用率"
        )
    
    # 实时系统资源
    st.markdown("#### 💻 系统资源")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CPU使用率
        cpu_usage = summary['cpu_usage']
        st.progress(cpu_usage / 100)
        st.markdown(f"**CPU使用率**: {cpu_usage:.1f}%")
    
    with col2:
        # 内存使用率
        memory_usage = summary['memory_usage']
        st.progress(memory_usage / 100)
        st.markdown(f"**内存使用率**: {memory_usage:.1f}%")
    
    # 性能趋势图表
    st.markdown("#### 📈 性能趋势")
    
    metrics = monitor.get_metrics(since=datetime.now() - timedelta(hours=1))
    
    if metrics:
        import pandas as pd
        import plotly.express as px
        
        # 准备数据
        df_data = []
        for metric in metrics:
            df_data.append({
                'timestamp': metric.timestamp,
                'name': metric.name,
                'value': metric.value,
                'category': metric.category
            })
        
        df = pd.DataFrame(df_data)
        
        if not df.empty:
            # 按类别分组显示
            categories = df['category'].unique()
            
            for category in categories:
                category_df = df[df['category'] == category]
                
                if len(category_df) > 1:
                    fig = px.line(
                        category_df,
                        x='timestamp',
                        y='value',
                        color='name',
                        title=f'{category.title()} 性能趋势',
                        labels={'value': '值', 'timestamp': '时间'}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 暂无性能数据")
    
    # 性能告警
    st.markdown("#### 🚨 性能告警")
    
    alerts = monitor.get_alerts()
    
    if alerts:
        for alert in reversed(alerts[-10:]):  # 显示最近10条告警
            severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
            
            st.markdown(f"""
            {severity_icon} **{alert['metric_name']}** 
            - 当前值: {alert['value']:.2f}{alert['unit']}
            - 阈值: {alert['threshold']:.2f}{alert['unit']}
            - 时间: {alert['timestamp'][:19]}
            """)
    else:
        st.success("✅ 暂无性能告警")
    
    # 操作按钮
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 刷新数据"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ 清除指标"):
            monitor.clear_metrics()
            st.success("✅ 性能指标已清除")
            st.rerun()
    
    with col3:
        if st.button("🔕 清除告警"):
            monitor.clear_alerts()
            st.success("✅ 性能告警已清除")
            st.rerun()

# 页面加载时间监控
def monitor_page_load():
    """监控页面加载时间"""
    if 'page_load_start' not in st.session_state:
        st.session_state.page_load_start = time.time()
    
    # 在页面渲染完成后记录加载时间
    load_time = time.time() - st.session_state.page_load_start
    
    record_metric(
        name="Page Load Time",
        value=load_time,
        unit="seconds",
        category="page_performance",
        metadata={
            'page': st.session_state.get('current_page', 'unknown'),
            'user': st.session_state.get('user', {}).get('email', 'anonymous')
        }
    )
    
    # 重置计时器
    st.session_state.page_load_start = time.time()

# API响应时间监控
def monitor_api_call(func: Callable, *args, **kwargs):
    """监控API调用时间"""
    with PerformanceTimer("API Response Time", "api_performance"):
        return func(*args, **kwargs)
