"""
统一缓存管理器
优化缓存性能和管理
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import threading
import time
import json
from dataclasses import dataclass

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    data: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None

class CacheManager:
    """统一缓存管理器"""
    
    def __init__(self):
        self.default_ttl = 300  # 5分钟
        self.max_cache_size = 1000  # 最大缓存条目数
        self.cleanup_interval = 60  # 清理间隔(秒)
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'cleanups': 0
        }
        
        # 初始化缓存存储
        self._init_cache_storage()
        
        # 启动后台清理任务
        self._start_cleanup_task()
    
    def _init_cache_storage(self):
        """初始化缓存存储"""
        if 'cache_storage' not in st.session_state:
            st.session_state.cache_storage = {}
        
        if 'cache_stats' not in st.session_state:
            st.session_state.cache_stats = self.stats.copy()
    
    def _start_cleanup_task(self):
        """启动后台清理任务"""
        # 注意：Streamlit中不能使用真正的后台线程
        # 这里只是在访问时检查是否需要清理
        pass
    
    def _should_cleanup(self) -> bool:
        """检查是否需要清理"""
        last_cleanup = getattr(self, '_last_cleanup', None)
        if not last_cleanup:
            self._last_cleanup = datetime.now()
            return True
        
        return (datetime.now() - last_cleanup).seconds > self.cleanup_interval
    
    def _cleanup_expired(self):
        """清理过期缓存"""
        if not self._should_cleanup():
            return
        
        current_time = datetime.now()
        cache_storage = st.session_state.cache_storage
        
        expired_keys = []
        for key, entry in cache_storage.items():
            if isinstance(entry, dict) and 'expires_at' in entry:
                # 兼容旧格式
                if current_time > datetime.fromisoformat(entry['expires_at']):
                    expired_keys.append(key)
            elif isinstance(entry, CacheEntry):
                if current_time > entry.expires_at:
                    expired_keys.append(key)
        
        # 删除过期条目
        for key in expired_keys:
            del cache_storage[key]
            st.session_state.cache_stats['evictions'] += 1
        
        # 如果缓存过大，删除最少使用的条目
        if len(cache_storage) > self.max_cache_size:
            self._evict_lru()
        
        self._last_cleanup = current_time
        st.session_state.cache_stats['cleanups'] += 1
    
    def _evict_lru(self):
        """删除最少使用的缓存条目"""
        cache_storage = st.session_state.cache_storage
        
        # 按访问次数和最后访问时间排序
        entries = []
        for key, entry in cache_storage.items():
            if isinstance(entry, CacheEntry):
                entries.append((key, entry.access_count, entry.last_accessed or entry.created_at))
            else:
                # 兼容旧格式
                entries.append((key, 0, datetime.now()))
        
        # 排序并删除最少使用的条目
        entries.sort(key=lambda x: (x[1], x[2]))
        
        # 删除10%的条目
        evict_count = max(1, len(entries) // 10)
        for i in range(evict_count):
            key = entries[i][0]
            if key in cache_storage:
                del cache_storage[key]
                st.session_state.cache_stats['evictions'] += 1
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        if ttl is None:
            ttl = self.default_ttl
        
        current_time = datetime.now()
        expires_at = current_time + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            data=data,
            created_at=current_time,
            expires_at=expires_at,
            access_count=0,
            last_accessed=current_time
        )
        
        st.session_state.cache_storage[key] = entry
        
        # 触发清理检查
        self._cleanup_expired()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_storage = st.session_state.cache_storage
        
        if key not in cache_storage:
            st.session_state.cache_stats['misses'] += 1
            return None
        
        entry = cache_storage[key]
        current_time = datetime.now()
        
        # 兼容旧格式
        if isinstance(entry, dict):
            if 'expires_at' in entry:
                expires_at = datetime.fromisoformat(entry['expires_at'])
                if current_time > expires_at:
                    del cache_storage[key]
                    st.session_state.cache_stats['misses'] += 1
                    return None
                
                st.session_state.cache_stats['hits'] += 1
                return entry.get('data')
        
        # 新格式
        elif isinstance(entry, CacheEntry):
            if current_time > entry.expires_at:
                del cache_storage[key]
                st.session_state.cache_stats['misses'] += 1
                return None
            
            # 更新访问统计
            entry.access_count += 1
            entry.last_accessed = current_time
            cache_storage[key] = entry
            
            st.session_state.cache_stats['hits'] += 1
            return entry.data
        
        # 未知格式，删除
        del cache_storage[key]
        st.session_state.cache_stats['misses'] += 1
        return None
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        cache_storage = st.session_state.cache_storage
        
        if key in cache_storage:
            del cache_storage[key]
            return True
        
        return False
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """清除缓存"""
        cache_storage = st.session_state.cache_storage
        
        if pattern is None:
            # 清除所有缓存
            count = len(cache_storage)
            cache_storage.clear()
            return count
        
        # 按模式清除
        keys_to_delete = []
        for key in cache_storage.keys():
            if pattern in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del cache_storage[key]
        
        return len(keys_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        cache_storage = st.session_state.cache_storage
        stats = st.session_state.cache_stats.copy()
        
        total_requests = stats['hits'] + stats['misses']
        hit_rate = (stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **stats,
            'total_entries': len(cache_storage),
            'hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total_requests
        }
    
    def get_cache_info(self) -> List[Dict[str, Any]]:
        """获取缓存详细信息"""
        cache_storage = st.session_state.cache_storage
        current_time = datetime.now()
        
        cache_info = []
        for key, entry in cache_storage.items():
            if isinstance(entry, CacheEntry):
                info = {
                    'key': key,
                    'size': len(str(entry.data)),
                    'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'expires_at': entry.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'ttl': max(0, (entry.expires_at - current_time).seconds),
                    'access_count': entry.access_count,
                    'last_accessed': entry.last_accessed.strftime('%Y-%m-%d %H:%M:%S') if entry.last_accessed else 'Never'
                }
            else:
                # 兼容旧格式
                info = {
                    'key': key,
                    'size': len(str(entry)),
                    'created_at': 'Unknown',
                    'expires_at': entry.get('expires_at', 'Unknown') if isinstance(entry, dict) else 'Unknown',
                    'ttl': 0,
                    'access_count': 0,
                    'last_accessed': 'Unknown'
                }
            
            cache_info.append(info)
        
        return cache_info

# 全局缓存管理器实例
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

# 便捷函数
def cache_set(key: str, data: Any, ttl: Optional[int] = None) -> None:
    """设置缓存"""
    get_cache_manager().set(key, data, ttl)

def cache_get(key: str) -> Optional[Any]:
    """获取缓存"""
    return get_cache_manager().get(key)

def cache_delete(key: str) -> bool:
    """删除缓存"""
    return get_cache_manager().delete(key)

def cache_clear(pattern: Optional[str] = None) -> int:
    """清除缓存"""
    return get_cache_manager().clear(pattern)

def cache_stats() -> Dict[str, Any]:
    """获取缓存统计"""
    return get_cache_manager().get_stats()

# 装饰器
def cached(ttl: int = 300, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = cache_get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
