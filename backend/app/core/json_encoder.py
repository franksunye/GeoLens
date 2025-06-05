"""
自定义JSON编码器

处理datetime等特殊对象的JSON序列化。
"""

import json
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理特殊类型的序列化"""
    
    def default(self, obj: Any) -> Any:
        """处理默认JSON编码器无法处理的对象类型"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, UUID):
            return str(obj)
        elif hasattr(obj, 'model_dump'):
            # Pydantic模型
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            # Pydantic v1模型
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            # 普通对象
            return obj.__dict__
        
        return super().default(obj)


def json_response_with_encoder(content: Any, status_code: int = 200) -> dict:
    """
    创建可以正确序列化的JSON响应内容
    
    Args:
        content: 要序列化的内容
        status_code: HTTP状态码
        
    Returns:
        可以安全序列化的字典
    """
    try:
        # 先尝试用自定义编码器序列化，然后反序列化
        # 这样可以确保所有对象都被正确转换
        json_str = json.dumps(content, cls=CustomJSONEncoder, ensure_ascii=False)
        return json.loads(json_str)
    except Exception as e:
        # 如果序列化失败，返回错误信息
        return {
            "error": "Serialization failed",
            "message": str(e),
            "original_type": str(type(content))
        }


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    安全的JSON序列化函数
    
    Args:
        obj: 要序列化的对象
        **kwargs: json.dumps的其他参数
        
    Returns:
        JSON字符串
    """
    kwargs.setdefault('cls', CustomJSONEncoder)
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 2)
    
    return json.dumps(obj, **kwargs)
