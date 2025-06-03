"""
反爬虫策略处理
"""

import random
import time
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class UserAgentPool:
    """用户代理池"""
    desktop_agents: List[str]
    mobile_agents: List[str]
    
    def get_random_desktop(self) -> str:
        return random.choice(self.desktop_agents)
    
    def get_random_mobile(self) -> str:
        return random.choice(self.mobile_agents)
    
    def get_random(self) -> str:
        all_agents = self.desktop_agents + self.mobile_agents
        return random.choice(all_agents)


class AntiBot:
    """反爬虫策略处理器"""
    
    def __init__(self):
        self.user_agent_pool = self._create_user_agent_pool()
        self.request_delays = {}
        self.request_counts = {}
        self.blocked_domains = set()
    
    def _create_user_agent_pool(self) -> UserAgentPool:
        """创建用户代理池"""
        desktop_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        
        mobile_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.193 Mobile Safari/537.36",
        ]
        
        return UserAgentPool(desktop_agents, mobile_agents)
    
    def get_headers(self, url: str, mobile: bool = False) -> Dict[str, str]:
        """获取反爬虫请求头"""
        if mobile:
            user_agent = self.user_agent_pool.get_random_mobile()
        else:
            user_agent = self.user_agent_pool.get_random_desktop()
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        return headers
    
    def calculate_delay(self, url: str, base_delay: float = 1.0) -> float:
        """计算请求延迟"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        if domain in self.blocked_domains:
            return base_delay * 10
        
        count = self.request_counts.get(domain, 0)
        
        if count > 100:
            delay_multiplier = 3.0
        elif count > 50:
            delay_multiplier = 2.0
        else:
            delay_multiplier = 1.0
        
        random_factor = random.uniform(0.5, 1.5)
        return base_delay * delay_multiplier * random_factor
    
    async def wait_if_needed(self, url: str, min_delay: float = 1.0) -> None:
        """如果需要的话等待一段时间"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        current_time = time.time()
        last_request_time = self.request_delays.get(domain, 0)
        
        elapsed = current_time - last_request_time
        delay = self.calculate_delay(url, min_delay)
        
        if elapsed < delay:
            wait_time = delay - elapsed
            await asyncio.sleep(wait_time)
        
        self.request_delays[domain] = time.time()
        self.request_counts[domain] = self.request_counts.get(domain, 0) + 1
    
    def mark_domain_blocked(self, url: str) -> None:
        """标记域名为被封状态"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        self.blocked_domains.add(domain)
    
    def is_domain_blocked(self, url: str) -> bool:
        """检查域名是否被封"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain in self.blocked_domains
    
    def reset_domain_status(self, url: str) -> None:
        """重置域名状态"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        self.blocked_domains.discard(domain)
        self.request_counts.pop(domain, None)
        self.request_delays.pop(domain, None)
    
    def detect_anti_bot_measures(self, html: str, status_code: int, headers: Dict[str, str]) -> List[str]:
        """检测反爬虫措施"""
        measures = []
        
        if status_code == 403:
            measures.append("HTTP_403_FORBIDDEN")
        elif status_code == 429:
            measures.append("RATE_LIMITED")
        elif status_code == 503:
            measures.append("SERVICE_UNAVAILABLE")
        
        if "cf-ray" in headers:
            measures.append("CLOUDFLARE_PROTECTION")
        
        if "server" in headers and "cloudflare" in headers["server"].lower():
            measures.append("CLOUDFLARE_SERVER")
        
        html_lower = html.lower()
        
        if "captcha" in html_lower:
            measures.append("CAPTCHA_CHALLENGE")
        
        if "cloudflare" in html_lower and "checking your browser" in html_lower:
            measures.append("CLOUDFLARE_BROWSER_CHECK")
        
        if "access denied" in html_lower or "blocked" in html_lower:
            measures.append("ACCESS_DENIED")
        
        return measures
