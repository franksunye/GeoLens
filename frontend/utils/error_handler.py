"""
统一错误处理中间件
标准化错误处理和用户反馈
"""

import streamlit as st
import traceback
import logging
from typing import Any, Callable, Optional, Dict
from functools import wraps
from datetime import datetime
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorType:
    """错误类型常量"""
    NETWORK_ERROR = "network_error"
    AUTH_ERROR = "auth_error"
    VALIDATION_ERROR = "validation_error"
    API_ERROR = "api_error"
    SYSTEM_ERROR = "system_error"
    USER_ERROR = "user_error"

class GeoLensError(Exception):
    """自定义异常基类"""
    
    def __init__(self, message: str, error_type: str = ErrorType.SYSTEM_ERROR, 
                 details: Optional[Dict] = None, recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = datetime.now()

class NetworkError(GeoLensError):
    """网络错误"""
    def __init__(self, message: str = "网络连接失败", **kwargs):
        super().__init__(message, ErrorType.NETWORK_ERROR, **kwargs)

class AuthError(GeoLensError):
    """认证错误"""
    def __init__(self, message: str = "认证失败", **kwargs):
        super().__init__(message, ErrorType.AUTH_ERROR, **kwargs)

class ValidationError(GeoLensError):
    """验证错误"""
    def __init__(self, message: str = "数据验证失败", **kwargs):
        super().__init__(message, ErrorType.VALIDATION_ERROR, **kwargs)

class APIError(GeoLensError):
    """API错误"""
    def __init__(self, message: str = "API调用失败", **kwargs):
        super().__init__(message, ErrorType.API_ERROR, **kwargs)

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_messages = {
            ErrorType.NETWORK_ERROR: {
                'title': '🌐 网络连接问题',
                'icon': '🔌',
                'color': 'warning',
                'suggestions': [
                    '检查网络连接是否正常',
                    '尝试刷新页面',
                    '稍后再试'
                ]
            },
            ErrorType.AUTH_ERROR: {
                'title': '🔐 认证失败',
                'icon': '🚫',
                'color': 'error',
                'suggestions': [
                    '请重新登录',
                    '检查账号密码是否正确',
                    '联系管理员获取帮助'
                ]
            },
            ErrorType.VALIDATION_ERROR: {
                'title': '📝 输入验证失败',
                'icon': '⚠️',
                'color': 'warning',
                'suggestions': [
                    '检查输入格式是否正确',
                    '确保必填字段已填写',
                    '参考输入示例'
                ]
            },
            ErrorType.API_ERROR: {
                'title': '🔗 服务调用失败',
                'icon': '🛠️',
                'color': 'error',
                'suggestions': [
                    '服务暂时不可用',
                    '请稍后重试',
                    '如问题持续，请联系技术支持'
                ]
            },
            ErrorType.SYSTEM_ERROR: {
                'title': '⚙️ 系统错误',
                'icon': '🔧',
                'color': 'error',
                'suggestions': [
                    '系统遇到未知错误',
                    '请刷新页面重试',
                    '如问题持续，请联系技术支持'
                ]
            },
            ErrorType.USER_ERROR: {
                'title': '👤 操作错误',
                'icon': '💡',
                'color': 'info',
                'suggestions': [
                    '请检查操作步骤',
                    '参考帮助文档',
                    '确认输入信息正确'
                ]
            }
        }
        
        # 初始化错误日志
        self._init_error_log()
    
    def _init_error_log(self):
        """初始化错误日志"""
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
    
    def _log_error(self, error: Exception, context: Optional[Dict] = None):
        """记录错误日志"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc() if not isinstance(error, GeoLensError) else None
        }
        
        # 添加到会话日志
        st.session_state.error_log.append(error_entry)
        
        # 保持最近100条错误记录
        if len(st.session_state.error_log) > 100:
            st.session_state.error_log = st.session_state.error_log[-100:]
        
        # 记录到系统日志
        logger.error(f"Error: {error_entry}")
    
    def handle_error(self, error: Exception, context: Optional[Dict] = None, 
                    show_details: bool = False) -> None:
        """处理错误并显示用户友好的消息"""
        
        # 记录错误
        self._log_error(error, context)
        
        # 确定错误类型和消息
        if isinstance(error, GeoLensError):
            error_type = error.error_type
            message = error.message
            recoverable = error.recoverable
            details = error.details
        else:
            error_type = ErrorType.SYSTEM_ERROR
            message = str(error)
            recoverable = True
            details = {}
        
        # 获取错误配置
        error_config = self.error_messages.get(error_type, self.error_messages[ErrorType.SYSTEM_ERROR])
        
        # 显示错误消息
        self._display_error(error_config, message, details, show_details, recoverable)
    
    def _display_error(self, config: Dict, message: str, details: Dict, 
                      show_details: bool, recoverable: bool):
        """显示错误消息"""
        
        # 错误标题和图标
        st.error(f"{config['icon']} **{config['title']}**")
        
        # 错误消息
        st.markdown(f"**错误信息**: {message}")
        
        # 建议操作
        if config['suggestions']:
            st.markdown("**建议操作**:")
            for suggestion in config['suggestions']:
                st.markdown(f"- {suggestion}")
        
        # 详细信息（可选）
        if show_details and details:
            with st.expander("🔍 详细信息", expanded=False):
                st.json(details)
        
        # 恢复操作
        if recoverable:
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("🔄 重试", key=f"retry_{id(message)}"):
                    st.rerun()
            
            with col2:
                if st.button("🏠 返回首页", key=f"home_{id(message)}"):
                    st.switch_page("main.py")
            
            with col3:
                if st.button("📞 联系支持", key=f"support_{id(message)}"):
                    st.info("📧 请发送邮件到: support@geolens.ai")
    
    def get_error_log(self) -> list:
        """获取错误日志"""
        return st.session_state.get('error_log', [])
    
    def clear_error_log(self):
        """清除错误日志"""
        st.session_state.error_log = []

# 全局错误处理器实例
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """获取错误处理器实例"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def handle_error(error: Exception, context: Optional[Dict] = None, 
                show_details: bool = False) -> None:
    """处理错误的便捷函数"""
    get_error_handler().handle_error(error, context, show_details)

def safe_execute(func: Callable, *args, context: Optional[Dict] = None, 
                default_return: Any = None, show_details: bool = False, **kwargs) -> Any:
    """安全执行函数，自动处理异常"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, context, show_details)
        return default_return

# 装饰器
def error_handler(context: Optional[Dict] = None, show_details: bool = False, 
                 default_return: Any = None):
    """错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_error(e, context, show_details)
                return default_return
        return wrapper
    return decorator

def validate_input(value: Any, validator: Callable, error_message: str) -> Any:
    """输入验证函数"""
    try:
        if not validator(value):
            raise ValidationError(error_message)
        return value
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"验证过程中发生错误: {str(e)}")

def require_auth(func):
    """需要认证的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            raise AuthError("请先登录后再进行此操作")
        return func(*args, **kwargs)
    return wrapper

# 常用验证器
class Validators:
    """常用验证器"""
    
    @staticmethod
    def not_empty(value: str) -> bool:
        """非空验证"""
        return bool(value and value.strip())
    
    @staticmethod
    def email_format(email: str) -> bool:
        """邮箱格式验证"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def min_length(min_len: int):
        """最小长度验证"""
        def validator(value: str) -> bool:
            return len(value) >= min_len
        return validator
    
    @staticmethod
    def max_length(max_len: int):
        """最大长度验证"""
        def validator(value: str) -> bool:
            return len(value) <= max_len
        return validator
    
    @staticmethod
    def in_choices(choices: list):
        """选择范围验证"""
        def validator(value: Any) -> bool:
            return value in choices
        return validator

# 错误恢复助手
class ErrorRecovery:
    """错误恢复助手"""
    
    @staticmethod
    def retry_with_backoff(func: Callable, max_retries: int = 3, 
                          backoff_factor: float = 1.0) -> Any:
        """带退避的重试机制"""
        import time
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = backoff_factor * (2 ** attempt)
                time.sleep(wait_time)
        
        return None
    
    @staticmethod
    def fallback_data(primary_func: Callable, fallback_func: Callable) -> Any:
        """主备数据源切换"""
        try:
            return primary_func()
        except Exception:
            try:
                return fallback_func()
            except Exception as e:
                raise APIError(f"主备数据源均不可用: {str(e)}")

def show_error_dashboard():
    """显示错误监控面板"""
    st.markdown("### 🐛 错误监控面板")
    
    error_handler = get_error_handler()
    error_log = error_handler.get_error_log()
    
    if not error_log:
        st.info("📊 暂无错误记录")
        return
    
    # 错误统计
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总错误数", len(error_log))
    
    with col2:
        recent_errors = [e for e in error_log if 
                        (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 3600]
        st.metric("最近1小时", len(recent_errors))
    
    with col3:
        error_types = {}
        for error in error_log:
            error_type = error['type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        most_common = max(error_types.items(), key=lambda x: x[1]) if error_types else ("无", 0)
        st.metric("最常见错误", f"{most_common[0]} ({most_common[1]})")
    
    # 错误列表
    st.markdown("#### 📋 错误记录")
    
    for i, error in enumerate(reversed(error_log[-10:])):  # 显示最近10条
        with st.expander(f"{error['timestamp'][:19]} - {error['type']}", expanded=False):
            st.markdown(f"**消息**: {error['message']}")
            if error['context']:
                st.markdown("**上下文**:")
                st.json(error['context'])
            if error['traceback']:
                st.markdown("**堆栈跟踪**:")
                st.code(error['traceback'])
    
    # 清除日志按钮
    if st.button("🗑️ 清除错误日志"):
        error_handler.clear_error_log()
        st.success("✅ 错误日志已清除")
        st.rerun()
