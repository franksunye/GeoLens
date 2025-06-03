"""
网页爬虫基础类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import time


class CrawlStatus(str, Enum):
    """爬取状态"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"
    INVALID_URL = "invalid_url"


@dataclass
class CrawlResult:
    """爬取结果数据结构"""
    url: str
    status: CrawlStatus
    content: str
    title: str
    meta_description: str
    meta_keywords: str
    headers: Dict[str, str]
    status_code: int
    response_time: float
    crawl_time: datetime
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CrawlError(Exception):
    """爬虫异常基类"""
    
    def __init__(self, message: str, url: str = None, status_code: int = None):
        self.message = message
        self.url = url
        self.status_code = status_code
        super().__init__(message)


class WebCrawler(ABC):
    """网页爬虫抽象基类"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
        self.timeout = kwargs.get("timeout", 30)
        self.max_retries = kwargs.get("max_retries", 3)
        self.retry_delay = kwargs.get("retry_delay", 1.0)
        self.user_agent = kwargs.get(
            "user_agent", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置参数"""
        pass
    
    @abstractmethod
    async def crawl(self, url: str, **kwargs) -> CrawlResult:
        """爬取单个网页"""
        pass
    
    @abstractmethod
    async def crawl_batch(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """批量爬取网页"""
        pass
    
    def _create_result(
        self,
        url: str,
        status: CrawlStatus,
        content: str = "",
        title: str = "",
        meta_description: str = "",
        meta_keywords: str = "",
        headers: Dict[str, str] = None,
        status_code: int = 0,
        start_time: float = None,
        error_message: str = None,
        metadata: Dict[str, Any] = None
    ) -> CrawlResult:
        """创建标准化爬取结果"""
        return CrawlResult(
            url=url,
            status=status,
            content=content,
            title=title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            headers=headers or {},
            status_code=status_code,
            response_time=time.time() - (start_time or time.time()),
            crawl_time=datetime.utcnow(),
            error_message=error_message,
            metadata=metadata or {}
        )
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    async def health_check(self, test_url: str = "https://httpbin.org/get") -> bool:
        """健康检查"""
        try:
            result = await self.crawl(test_url)
            return result.status == CrawlStatus.SUCCESS
        except Exception:
            return False
