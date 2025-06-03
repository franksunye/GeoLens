"""
内容处理模块测试

测试内容提取、解析和格式化功能。
"""

import pytest
from app.services.content_processing import ContentExtractor


class TestContentExtractor:
    """内容提取器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.extractor = ContentExtractor()
    
    def test_extractor_initialization(self):
        """测试内容提取器初始化"""
        assert self.extractor is not None
        assert hasattr(self.extractor, 'extract')
    
    def test_extract_simple_text(self):
        """测试简单文本提取"""
        content = "这是一个简单的测试内容。"
        result = self.extractor.extract(content)
        
        assert result is not None
        assert result.main_content == content
        assert result.word_count > 0
    
    def test_extract_html_content(self):
        """测试HTML内容提取"""
        html_content = """
        <html>
            <head>
                <title>测试标题</title>
                <meta name="description" content="测试描述">
            </head>
            <body>
                <h1>主标题</h1>
                <p>这是测试段落内容。</p>
                <h2>副标题</h2>
                <p>更多内容。</p>
            </body>
        </html>
        """
        
        result = self.extractor.extract(html_content)
        
        assert result is not None
        assert result.title == "测试标题"
        assert result.meta_description == "测试描述"
        assert "主标题" in result.main_content
        assert "测试段落内容" in result.main_content
        assert len(result.headings) >= 2
    
    def test_extract_with_url(self):
        """测试带URL的内容提取"""
        content = "测试内容"
        url = "https://example.com"
        
        result = self.extractor.extract(content, url)
        
        assert result is not None
        assert result.main_content == content
    
    def test_extract_empty_content(self):
        """测试空内容提取"""
        result = self.extractor.extract("")
        
        assert result is not None
        assert result.main_content == ""
        assert result.word_count == 0
    
    def test_extract_content_with_special_characters(self):
        """测试包含特殊字符的内容提取"""
        content = "测试内容 @#$%^&*() 123 ABC"
        result = self.extractor.extract(content)
        
        assert result is not None
        assert result.main_content == content
        assert result.word_count > 0
    
    def test_extract_long_content(self):
        """测试长内容提取"""
        content = "这是一个很长的测试内容。" * 100
        result = self.extractor.extract(content)
        
        assert result is not None
        assert result.main_content == content
        assert result.word_count > 100
        assert result.reading_time > 0
    
    def test_extract_content_with_headings(self):
        """测试包含标题的内容提取"""
        html_content = """
        <h1>主标题</h1>
        <h2>二级标题</h2>
        <h3>三级标题</h3>
        <p>段落内容</p>
        """
        
        result = self.extractor.extract(html_content)
        
        assert result is not None
        assert len(result.headings) == 3
        assert "主标题" in result.headings
        assert "二级标题" in result.headings
        assert "三级标题" in result.headings
    
    def test_extract_content_with_links(self):
        """测试包含链接的内容提取"""
        html_content = """
        <p>这是一个包含<a href="https://example.com">链接</a>的段落。</p>
        <p>还有<a href="/internal">内部链接</a>。</p>
        """
        
        result = self.extractor.extract(html_content)
        
        assert result is not None
        assert len(result.links) >= 2
    
    def test_extract_content_with_images(self):
        """测试包含图片的内容提取"""
        html_content = """
        <p>这是一个包含图片的段落。</p>
        <img src="image1.jpg" alt="图片1">
        <img src="image2.png" alt="图片2">
        """
        
        result = self.extractor.extract(html_content)
        
        assert result is not None
        assert len(result.images) >= 2


class TestContentProcessingIntegration:
    """内容处理集成测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.extractor = ContentExtractor()
    
    def test_full_content_processing_pipeline(self):
        """测试完整的内容处理流水线"""
        # 模拟用户输入的内容
        content = """
        <html>
            <head>
                <title>GEO优化指南</title>
                <meta name="description" content="学习如何优化内容以适应生成式AI">
            </head>
            <body>
                <h1>GEO优化指南</h1>
                <p>生成式引擎优化(GEO)是一种新的优化方式。</p>
                <h2>什么是GEO？</h2>
                <p>GEO旨在提升品牌在生成式AI中被推荐的可见性。</p>
                <h2>GEO vs SEO</h2>
                <p>GEO专注于AI理解，而SEO专注于搜索引擎。</p>
            </body>
        </html>
        """
        
        # 执行内容提取
        result = self.extractor.extract(content)
        
        # 验证提取结果
        assert result is not None
        assert result.title == "GEO优化指南"
        assert result.meta_description == "学习如何优化内容以适应生成式AI"
        assert "生成式引擎优化" in result.main_content
        assert len(result.headings) >= 3
        assert result.word_count > 0
        assert result.reading_time > 0
    
    def test_content_processing_error_handling(self):
        """测试内容处理错误处理"""
        # 测试None输入
        result = self.extractor.extract(None)
        assert result is not None
        
        # 测试无效HTML
        invalid_html = "<html><head><title>测试</title><body><p>未闭合段落"
        result = self.extractor.extract(invalid_html)
        assert result is not None
    
    def test_content_processing_performance(self):
        """测试内容处理性能"""
        import time
        
        # 大量内容测试
        large_content = "<p>" + "测试内容 " * 1000 + "</p>"
        
        start_time = time.time()
        result = self.extractor.extract(large_content)
        end_time = time.time()
        
        # 处理时间应该在合理范围内（小于1秒）
        processing_time = end_time - start_time
        assert processing_time < 1.0
        assert result is not None
        assert result.word_count > 1000
