"""
网页爬虫单元测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx

from app.services.crawler import HTMLCrawler, ContentExtractor, AntiBot, CrawlStatus


class TestHTMLCrawler:
    """HTML爬虫测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.crawler = HTMLCrawler()
    
    def test_crawler_initialization(self):
        """测试爬虫初始化"""
        assert self.crawler.timeout == 30
        assert self.crawler.max_retries == 3
        assert self.crawler.follow_redirects is True
    
    def test_custom_config(self):
        """测试自定义配置"""
        crawler = HTMLCrawler(
            timeout=60,
            max_retries=5,
            follow_redirects=False
        )
        assert crawler.timeout == 60
        assert crawler.max_retries == 5
        assert crawler.follow_redirects is False
    
    def test_validate_config_invalid_timeout(self):
        """测试无效超时配置"""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            HTMLCrawler(timeout=0)
    
    def test_validate_config_invalid_retries(self):
        """测试无效重试配置"""
        with pytest.raises(ValueError, match="Max retries must be non-negative"):
            HTMLCrawler(max_retries=-1)
    
    def test_get_headers(self):
        """测试请求头生成"""
        headers = self.crawler._get_headers("https://example.com")
        
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Referer" in headers
        assert headers["Referer"] == "https://example.com/"
    
    def test_extract_meta_info(self):
        """测试元信息提取"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
                <meta name="keywords" content="test, page, example">
            </head>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        meta_info = self.crawler._extract_meta_info(soup)
        
        assert meta_info["title"] == "Test Page"
        assert meta_info["description"] == "Test description"
        assert meta_info["keywords"] == "test, page, example"
    
    @pytest.mark.asyncio
    async def test_crawl_invalid_url(self):
        """测试无效URL"""
        result = await self.crawler.crawl("invalid-url")
        
        assert result.status == CrawlStatus.INVALID_URL
        assert "Invalid URL format" in result.error_message
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_crawl_success(self, mock_client):
        """测试成功爬取"""
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <h1>Main Title</h1>
                <p>Test content</p>
            </body>
        </html>
        """
        mock_response.headers = {"content-type": "text/html"}
        mock_response.url = "https://example.com"
        mock_response.encoding = "utf-8"
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await self.crawler.crawl("https://example.com")
        
        assert result.status == CrawlStatus.SUCCESS
        assert result.title == "Test Page"
        assert "Test content" in result.content
        assert result.status_code == 200
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_crawl_blocked(self, mock_client):
        """测试被封禁"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.reason_phrase = "Forbidden"
        mock_response.headers = {}
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await self.crawler.crawl("https://example.com")
        
        assert result.status == CrawlStatus.BLOCKED
        assert result.status_code == 403
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_crawl_timeout(self, mock_client):
        """测试超时"""
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = httpx.TimeoutException("Timeout")
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await self.crawler.crawl("https://example.com")
        
        assert result.status == CrawlStatus.FAILED
        assert "timeout" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_crawl_batch(self):
        """测试批量爬取"""
        urls = [
            "https://example1.com",
            "https://example2.com"
        ]
        
        with patch.object(self.crawler, 'crawl') as mock_crawl:
            mock_crawl.side_effect = [
                Mock(status=CrawlStatus.SUCCESS, url="https://example1.com"),
                Mock(status=CrawlStatus.SUCCESS, url="https://example2.com")
            ]
            
            results = await self.crawler.crawl_batch(urls)
            
            assert len(results) == 2
            assert all(r.status == CrawlStatus.SUCCESS for r in results)
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        with patch.object(self.crawler, 'crawl') as mock_crawl:
            mock_crawl.return_value = Mock(status=CrawlStatus.SUCCESS)
            
            is_healthy = await self.crawler.health_check()
            assert is_healthy is True
            
            mock_crawl.return_value = Mock(status=CrawlStatus.FAILED)
            is_healthy = await self.crawler.health_check()
            assert is_healthy is False


class TestContentExtractor:
    """内容提取器测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.extractor = ContentExtractor()
    
    def test_extract_basic_content(self):
        """测试基本内容提取"""
        html = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
                <meta name="keywords" content="test, page">
            </head>
            <body>
                <h1>Main Title</h1>
                <h2>Subtitle</h2>
                <p>This is test content.</p>
                <a href="https://example.com">External Link</a>
                <img src="image.jpg" alt="Test Image">
            </body>
        </html>
        """
        
        result = self.extractor.extract(html, "https://test.com")
        
        assert result.title == "Test Page"
        assert result.meta_description == "Test description"
        assert "test" in result.meta_keywords
        assert "page" in result.meta_keywords
        assert "This is test content." in result.main_content
        assert len(result.headings["h1"]) == 1
        assert len(result.headings["h2"]) == 1
        assert len(result.links) == 1
        assert len(result.images) == 1
    
    def test_clean_html(self):
        """测试HTML清理"""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <script>alert('test');</script>
                <style>body { color: red; }</style>
                <div class="advertisement">Ad content</div>
                <p>Real content</p>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        self.extractor._clean_html(soup)
        
        # 检查script和style标签被移除
        assert soup.find('script') is None
        assert soup.find('style') is None
        
        # 检查广告内容被移除
        assert soup.find('div', class_='advertisement') is None
        
        # 检查真实内容保留
        assert soup.find('p') is not None
    
    def test_extract_title_priority(self):
        """测试标题提取优先级"""
        from bs4 import BeautifulSoup
        
        # H1优先级最高
        html_h1 = """
        <html>
            <head><title>Title Tag</title></head>
            <body><h1>H1 Title</h1></body>
        </html>
        """
        soup = BeautifulSoup(html_h1, 'html.parser')
        title = self.extractor._extract_title(soup)
        assert title == "H1 Title"
        
        # 没有H1时使用title标签
        html_title = """
        <html>
            <head><title>Title Tag</title></head>
            <body><h2>H2 Title</h2></body>
        </html>
        """
        soup = BeautifulSoup(html_title, 'html.parser')
        title = self.extractor._extract_title(soup)
        assert title == "Title Tag"
    
    def test_extract_links(self):
        """测试链接提取"""
        html = """
        <html>
            <body>
                <a href="https://external.com" title="External">External Link</a>
                <a href="/internal" rel="nofollow">Internal Link</a>
                <a href="mailto:test@example.com">Email Link</a>
            </body>
        </html>
        """
        
        result = self.extractor.extract(html, "https://test.com")
        
        assert len(result.links) == 3
        
        # 检查外部链接
        external_link = next(l for l in result.links if "external.com" in l["url"])
        assert external_link["text"] == "External Link"
        assert external_link["title"] == "External"
        
        # 检查内部链接转换为绝对URL
        internal_link = next(l for l in result.links if "/internal" in l["url"])
        assert internal_link["url"] == "https://test.com/internal"
        assert internal_link["rel"] == "nofollow"
    
    def test_extract_images(self):
        """测试图片提取"""
        html = """
        <html>
            <body>
                <img src="https://example.com/image1.jpg" alt="Image 1" width="100" height="200">
                <img src="/local/image2.png" title="Local Image">
                <img src="data:image/gif;base64,R0lGOD...">
            </body>
        </html>
        """
        
        result = self.extractor.extract(html, "https://test.com")
        
        assert len(result.images) == 3
        
        # 检查绝对URL图片
        abs_img = next(i for i in result.images if "example.com" in i["url"])
        assert abs_img["alt"] == "Image 1"
        assert abs_img["width"] == "100"
        assert abs_img["height"] == "200"
        
        # 检查相对URL转换
        rel_img = next(i for i in result.images if "local/image2.png" in i["url"])
        assert rel_img["url"] == "https://test.com/local/image2.png"
        assert rel_img["title"] == "Local Image"
    
    def test_word_count_and_reading_time(self):
        """测试单词计数和阅读时间"""
        html = """
        <html>
            <body>
                <p>This is a test paragraph with exactly ten words here.</p>
                <p>Another paragraph with some more words to count properly.</p>
            </body>
        </html>
        """
        
        result = self.extractor.extract(html)
        
        assert result.word_count > 0
        assert result.reading_time > 0
        # 200 words per minute is default
        expected_time = max(1, round(result.word_count / 200))
        assert result.reading_time == expected_time


class TestAntiBot:
    """反爬虫策略测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.anti_bot = AntiBot()
    
    def test_user_agent_pool(self):
        """测试用户代理池"""
        desktop_agent = self.anti_bot.user_agent_pool.get_random_desktop()
        mobile_agent = self.anti_bot.user_agent_pool.get_random_mobile()
        random_agent = self.anti_bot.user_agent_pool.get_random()
        
        assert desktop_agent
        assert mobile_agent
        assert random_agent
        assert "Chrome" in desktop_agent or "Firefox" in desktop_agent
        assert "Mobile" in mobile_agent or "iPhone" in mobile_agent
    
    def test_get_headers(self):
        """测试请求头生成"""
        headers = self.anti_bot.get_headers("https://example.com")
        
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Accept-Language" in headers
        assert "Connection" in headers
        
        # 测试移动端请求头
        mobile_headers = self.anti_bot.get_headers("https://example.com", mobile=True)
        assert "Mobile" in mobile_headers["User-Agent"] or "iPhone" in mobile_headers["User-Agent"]
    
    def test_calculate_delay(self):
        """测试延迟计算"""
        url = "https://example.com"
        
        # 首次请求延迟较短
        delay1 = self.anti_bot.calculate_delay(url)
        assert delay1 >= 0.5  # 至少有随机因子
        
        # 增加请求计数
        self.anti_bot.request_counts["example.com"] = 60
        delay2 = self.anti_bot.calculate_delay(url)
        assert delay2 > delay1  # 高频请求延迟更长
    
    @pytest.mark.asyncio
    async def test_wait_if_needed(self):
        """测试等待机制"""
        import time
        
        url = "https://test.com"
        start_time = time.time()
        
        await self.anti_bot.wait_if_needed(url, min_delay=0.1)
        
        elapsed = time.time() - start_time
        assert elapsed >= 0.05  # 至少等待了一些时间
        
        # 检查请求时间和计数被更新
        assert "test.com" in self.anti_bot.request_delays
        assert "test.com" in self.anti_bot.request_counts
    
    def test_domain_blocking(self):
        """测试域名封禁"""
        url = "https://blocked.com"
        
        # 初始状态未被封
        assert not self.anti_bot.is_domain_blocked(url)
        
        # 标记为被封
        self.anti_bot.mark_domain_blocked(url)
        assert self.anti_bot.is_domain_blocked(url)
        
        # 重置状态
        self.anti_bot.reset_domain_status(url)
        assert not self.anti_bot.is_domain_blocked(url)
    
    def test_detect_anti_bot_measures(self):
        """测试反爬虫措施检测"""
        # 测试Cloudflare检测
        html_cf = "Please wait while we check your browser... Cloudflare"
        headers_cf = {"server": "cloudflare", "cf-ray": "12345"}
        measures = self.anti_bot.detect_anti_bot_measures(html_cf, 200, headers_cf)
        
        assert "CLOUDFLARE_PROTECTION" in measures
        assert "CLOUDFLARE_SERVER" in measures
        assert "CLOUDFLARE_BROWSER_CHECK" in measures
        
        # 测试CAPTCHA检测
        html_captcha = "Please solve the captcha below"
        measures = self.anti_bot.detect_anti_bot_measures(html_captcha, 200, {})
        assert "CAPTCHA_CHALLENGE" in measures
        
        # 测试状态码检测
        measures = self.anti_bot.detect_anti_bot_measures("", 403, {})
        assert "HTTP_403_FORBIDDEN" in measures
        
        measures = self.anti_bot.detect_anti_bot_measures("", 429, {})
        assert "RATE_LIMITED" in measures
