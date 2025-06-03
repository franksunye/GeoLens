"""
内容提取器
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass
class ExtractedContent:
    """提取的内容数据结构"""
    title: str
    main_content: str
    meta_description: str
    meta_keywords: List[str]
    headings: Dict[str, List[str]]
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    schema_org: Dict[str, Any]
    word_count: int
    reading_time: int
    language: Optional[str]
    author: Optional[str]
    publish_date: Optional[str]


class ContentExtractor:
    """内容提取器"""
    
    def __init__(self):
        self.remove_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside']
        self.content_selectors = ['article', 'main', '.content', '#content']
    
    def extract(self, html: str, base_url: str = "") -> ExtractedContent:
        """从HTML中提取内容"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 清理HTML
        self._clean_html(soup)
        
        # 提取各种内容
        title = self._extract_title(soup)
        main_content = self._extract_main_content(soup)
        meta_description = self._extract_meta_description(soup)
        meta_keywords = self._extract_meta_keywords(soup)
        headings = self._extract_headings(soup)
        links = self._extract_links(soup, base_url)
        images = self._extract_images(soup, base_url)
        schema_org = self._extract_schema_org(soup)
        
        # 计算统计信息
        word_count = self._count_words(main_content)
        reading_time = self._estimate_reading_time(word_count)
        
        # 提取元信息
        language = self._extract_language(soup)
        author = self._extract_author(soup)
        publish_date = self._extract_publish_date(soup)
        
        return ExtractedContent(
            title=title,
            main_content=main_content,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            headings=headings,
            links=links,
            images=images,
            schema_org=schema_org,
            word_count=word_count,
            reading_time=reading_time,
            language=language,
            author=author,
            publish_date=publish_date
        )
    
    def _clean_html(self, soup: BeautifulSoup) -> None:
        """清理HTML"""
        for tag_name in self.remove_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        
        return ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """提取主要内容"""
        for selector in self.content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                return self._clean_text(content_element.get_text())
        
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text())
        
        return self._clean_text(soup.get_text())
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """提取meta描述"""
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc and desc.get('content'):
            return desc['content'].strip()
        return ""
    
    def _extract_meta_keywords(self, soup: BeautifulSoup) -> List[str]:
        """提取meta关键词"""
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords and keywords.get('content'):
            return [k.strip() for k in keywords['content'].split(',') if k.strip()]
        return []
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """提取标题层级"""
        headings = {}
        for i in range(1, 7):
            tag_name = f'h{i}'
            tags = soup.find_all(tag_name)
            headings[tag_name] = [tag.get_text().strip() for tag in tags]
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """提取链接"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if base_url:
                href = urljoin(base_url, href)
            
            links.append({
                'url': href,
                'text': link.get_text().strip(),
                'title': link.get('title', ''),
                'rel': ' '.join(link.get('rel', []))
            })
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """提取图片"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if base_url:
                src = urljoin(base_url, src)
            
            images.append({
                'url': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        return images
    
    def _extract_schema_org(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """提取Schema.org结构化数据"""
        schema_data = {}
        
        # JSON-LD格式
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    schema_data.update(data)
            except:
                continue
        
        return schema_data
    
    def _extract_language(self, soup: BeautifulSoup) -> Optional[str]:
        """提取页面语言"""
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag['lang']
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """提取作者信息"""
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            return author_meta['content'].strip()
        return None
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """提取发布日期"""
        date_meta = soup.find('meta', attrs={'property': 'article:published_time'})
        if date_meta and date_meta.get('content'):
            return date_meta['content']
        return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _count_words(self, text: str) -> int:
        """计算单词数"""
        if not text:
            return 0
        words = text.split()
        return len(words)
    
    def _estimate_reading_time(self, word_count: int, wpm: int = 200) -> int:
        """估算阅读时间（分钟）"""
        if word_count == 0:
            return 0
        return max(1, round(word_count / wpm))
