"""
HTML网页爬虫实现
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import random

import httpx
from bs4 import BeautifulSoup

from .base import WebCrawler, CrawlResult, CrawlError, CrawlStatus


class HTMLCrawler(WebCrawler):
    """HTML网页爬虫"""
    
    def __init__(self, **kwargs):
        self.follow_redirects = kwargs.get("follow_redirects", True)
        self.max_content_size = kwargs.get("max_content_size", 10 * 1024 * 1024)  # 10MB
        super().__init__(**kwargs)
    
    def _validate_config(self) -> None:
        """验证配置参数"""
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
    
    def _get_headers(self, url: str = None) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # 添加Referer头
        if url:
            parsed = urlparse(url)
            if parsed.netloc:
                headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
        
        return headers
    
    def _extract_meta_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """提取页面元信息"""
        meta_info = {
            "title": "",
            "description": "",
            "keywords": ""
        }
        
        # 提取标题
        title_tag = soup.find("title")
        if title_tag:
            meta_info["title"] = title_tag.get_text().strip()
        
        # 提取meta描述
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            meta_info["description"] = desc_tag["content"].strip()
        
        # 提取meta关键词
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag and keywords_tag.get("content"):
            meta_info["keywords"] = keywords_tag["content"].strip()
        
        return meta_info
    
    async def crawl(self, url: str, **kwargs) -> CrawlResult:
        """爬取单个网页"""
        start_time = time.time()
        
        # 验证URL
        if not self._is_valid_url(url):
            return self._create_result(
                url=url,
                status=CrawlStatus.INVALID_URL,
                error_message="Invalid URL format",
                start_time=start_time
            )
        
        # 重试机制
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
                
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=self.follow_redirects,
                    limits=httpx.Limits(max_connections=10)
                ) as client:
                    response = await client.get(
                        url,
                        headers=self._get_headers(url)
                    )
                    
                    # 检查响应状态
                    if response.status_code >= 400:
                        if response.status_code == 403:
                            return self._create_result(
                                url=url,
                                status=CrawlStatus.BLOCKED,
                                status_code=response.status_code,
                                headers=dict(response.headers),
                                error_message=f"Access blocked: {response.status_code}",
                                start_time=start_time
                            )
                        else:
                            raise CrawlError(
                                f"HTTP {response.status_code}",
                                url=url,
                                status_code=response.status_code
                            )
                    
                    # 获取内容
                    content = response.text
                    if len(content.encode('utf-8')) > self.max_content_size:
                        content = content[:self.max_content_size // 2]
                    
                    # 解析HTML
                    soup = BeautifulSoup(content, 'html.parser')
                    meta_info = self._extract_meta_info(soup)
                    
                    return self._create_result(
                        url=url,
                        status=CrawlStatus.SUCCESS,
                        content=content,
                        title=meta_info["title"],
                        meta_description=meta_info["description"],
                        meta_keywords=meta_info["keywords"],
                        headers=dict(response.headers),
                        status_code=response.status_code,
                        start_time=start_time,
                        metadata={
                            "final_url": str(response.url),
                            "encoding": response.encoding,
                            "content_type": response.headers.get("content-type", ""),
                            "content_length": len(content)
                        }
                    )
                    
            except httpx.TimeoutException:
                last_error = CrawlError(f"Request timeout after {self.timeout}s", url=url)
            except httpx.RequestError as e:
                last_error = CrawlError(f"Request failed: {str(e)}", url=url)
            except Exception as e:
                last_error = CrawlError(f"Unexpected error: {str(e)}", url=url)
        
        # 所有重试都失败了
        return self._create_result(
            url=url,
            status=CrawlStatus.FAILED,
            error_message=last_error.message if last_error else "Unknown error",
            start_time=start_time
        )
    
    async def crawl_batch(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """批量爬取网页"""
        max_concurrent = kwargs.get("max_concurrent", 5)
        delay_between_requests = kwargs.get("delay_between_requests", 1.0)
        
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(url: str) -> CrawlResult:
            async with semaphore:
                result = await self.crawl(url)
                if delay_between_requests > 0:
                    await asyncio.sleep(delay_between_requests)
                return result
        
        # 并发执行爬取任务
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    self._create_result(
                        url=urls[i],
                        status=CrawlStatus.FAILED,
                        error_message=str(result)
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
