"""
内容分析器
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import Counter

from ..content_processing.content_extractor import ExtractedContent


@dataclass
class SEOAnalysis:
    """SEO分析结果"""
    title_length: int
    title_score: float
    meta_description_length: int
    meta_description_score: float
    heading_structure_score: float
    keyword_density: Dict[str, float]
    internal_links_count: int
    external_links_count: int
    images_without_alt: int
    schema_org_present: bool
    
    def overall_score(self) -> float:
        """计算总体SEO评分"""
        scores = [
            self.title_score,
            self.meta_description_score,
            self.heading_structure_score,
        ]
        return sum(scores) / len(scores)


@dataclass
class ReadabilityAnalysis:
    """可读性分析结果"""
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_words_per_sentence: float
    avg_sentences_per_paragraph: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    readability_score: float
    
    def get_reading_level(self) -> str:
        """获取阅读难度等级"""
        if self.flesch_reading_ease >= 90:
            return "Very Easy"
        elif self.flesch_reading_ease >= 80:
            return "Easy"
        elif self.flesch_reading_ease >= 70:
            return "Fairly Easy"
        elif self.flesch_reading_ease >= 60:
            return "Standard"
        elif self.flesch_reading_ease >= 50:
            return "Fairly Difficult"
        elif self.flesch_reading_ease >= 30:
            return "Difficult"
        else:
            return "Very Difficult"


@dataclass
class StructureAnalysis:
    """结构分析结果"""
    heading_hierarchy: Dict[str, int]
    heading_structure_issues: List[str]
    content_sections: int
    list_count: int
    table_count: int
    structure_score: float


@dataclass
class AnalysisResult:
    """综合分析结果"""
    url: str
    seo_analysis: SEOAnalysis
    readability_analysis: ReadabilityAnalysis
    structure_analysis: StructureAnalysis
    content_quality_score: float
    recommendations: List[str]
    
    def overall_score(self) -> float:
        """计算总体评分"""
        return (
            self.seo_analysis.overall_score() * 0.4 +
            self.readability_analysis.readability_score * 0.3 +
            self.structure_analysis.structure_score * 0.3
        )


class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
    
    def analyze(self, content: ExtractedContent, target_keywords: List[str] = None) -> AnalysisResult:
        """分析内容"""
        target_keywords = target_keywords or []
        
        # SEO分析
        seo_analysis = self._analyze_seo(content, target_keywords)
        
        # 可读性分析
        readability_analysis = self._analyze_readability(content.main_content)
        
        # 结构分析
        structure_analysis = self._analyze_structure(content)
        
        # 内容质量评分
        content_quality_score = self._calculate_content_quality(content)
        
        # 生成建议
        recommendations = self._generate_recommendations(content, seo_analysis)
        
        return AnalysisResult(
            url="",
            seo_analysis=seo_analysis,
            readability_analysis=readability_analysis,
            structure_analysis=structure_analysis,
            content_quality_score=content_quality_score,
            recommendations=recommendations
        )
    
    def _analyze_seo(self, content: ExtractedContent, target_keywords: List[str]) -> SEOAnalysis:
        """SEO分析"""
        title_length = len(content.title)
        title_score = self._score_title_length(title_length)
        
        meta_desc_length = len(content.meta_description)
        meta_desc_score = self._score_meta_description_length(meta_desc_length)
        
        heading_structure_score = self._score_heading_structure(content.headings)
        
        keyword_density = self._calculate_keyword_density(content.main_content, target_keywords)
        
        internal_links = sum(1 for link in content.links if self._is_internal_link(link['url']))
        external_links = len(content.links) - internal_links
        
        images_without_alt = sum(1 for img in content.images if not img['alt'])
        
        schema_org_present = bool(content.schema_org)
        
        return SEOAnalysis(
            title_length=title_length,
            title_score=title_score,
            meta_description_length=meta_desc_length,
            meta_description_score=meta_desc_score,
            heading_structure_score=heading_structure_score,
            keyword_density=keyword_density,
            internal_links_count=internal_links,
            external_links_count=external_links,
            images_without_alt=images_without_alt,
            schema_org_present=schema_org_present
        )
    
    def _analyze_readability(self, text: str) -> ReadabilityAnalysis:
        """可读性分析"""
        if not text:
            return ReadabilityAnalysis(0, 0, 0, 0, 0, 0, 0, 0)
        
        words = self._count_words(text)
        sentences = self._count_sentences(text)
        paragraphs = self._count_paragraphs(text)
        syllables = self._count_syllables(text)
        
        avg_words_per_sentence = words / max(sentences, 1)
        avg_sentences_per_paragraph = sentences / max(paragraphs, 1)
        
        # Flesch Reading Ease
        flesch_reading_ease = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * (syllables / max(words, 1)))
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))
        
        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = (0.39 * avg_words_per_sentence) + (11.8 * (syllables / max(words, 1))) - 15.59
        flesch_kincaid_grade = max(0, flesch_kincaid_grade)
        
        readability_score = flesch_reading_ease / 100
        
        return ReadabilityAnalysis(
            word_count=words,
            sentence_count=sentences,
            paragraph_count=paragraphs,
            avg_words_per_sentence=avg_words_per_sentence,
            avg_sentences_per_paragraph=avg_sentences_per_paragraph,
            flesch_reading_ease=flesch_reading_ease,
            flesch_kincaid_grade=flesch_kincaid_grade,
            readability_score=readability_score
        )
    
    def _analyze_structure(self, content: ExtractedContent) -> StructureAnalysis:
        """结构分析"""
        heading_hierarchy = {}
        for level, headings in content.headings.items():
            heading_hierarchy[level] = len(headings)
        
        structure_issues = []
        if heading_hierarchy.get('h1', 0) == 0:
            structure_issues.append("Missing H1 tag")
        elif heading_hierarchy.get('h1', 0) > 1:
            structure_issues.append("Multiple H1 tags")
        
        content_sections = max(1, content.main_content.count('\n\n'))
        list_count = content.main_content.count('•') + content.main_content.count('1.')
        table_count = content.main_content.count('|')
        
        structure_score = self._calculate_structure_score(heading_hierarchy, structure_issues)
        
        return StructureAnalysis(
            heading_hierarchy=heading_hierarchy,
            heading_structure_issues=structure_issues,
            content_sections=content_sections,
            list_count=list_count,
            table_count=table_count,
            structure_score=structure_score
        )
    
    def _score_title_length(self, length: int) -> float:
        """评分标题长度"""
        if 30 <= length <= 60:
            return 1.0
        elif 20 <= length < 30 or 60 < length <= 70:
            return 0.8
        else:
            return 0.3
    
    def _score_meta_description_length(self, length: int) -> float:
        """评分Meta描述长度"""
        if 120 <= length <= 160:
            return 1.0
        elif 100 <= length < 120 or 160 < length <= 180:
            return 0.8
        else:
            return 0.3
    
    def _score_heading_structure(self, headings: Dict[str, List[str]]) -> float:
        """评分标题结构"""
        score = 0.0
        
        h1_count = len(headings.get('h1', []))
        if h1_count == 1:
            score += 0.4
        
        if headings.get('h2'):
            score += 0.3
        
        has_structure = any(headings.get(f'h{i}') for i in range(2, 7))
        if has_structure:
            score += 0.3
        
        return min(1.0, score)
    
    def _calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """计算关键词密度"""
        if not text or not keywords:
            return {}
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        
        density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            density[keyword] = (count / max(total_words, 1)) * 100
        
        return density
    
    def _is_internal_link(self, url: str) -> bool:
        """判断是否为内部链接"""
        return not url.startswith(('http://', 'https://')) or url.startswith('#')
    
    def _count_words(self, text: str) -> int:
        """计算单词数"""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _count_sentences(self, text: str) -> int:
        """计算句子数"""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _count_paragraphs(self, text: str) -> int:
        """计算段落数"""
        paragraphs = text.split('\n\n')
        return len([p for p in paragraphs if p.strip()])
    
    def _count_syllables(self, text: str) -> int:
        """计算音节数（简化实现）"""
        words = re.findall(r'\b\w+\b', text.lower())
        syllable_count = 0
        
        for word in words:
            vowels = 'aeiouy'
            syllables = 0
            prev_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    syllables += 1
                prev_was_vowel = is_vowel
            
            syllables = max(1, syllables)
            if word.endswith('e') and syllables > 1:
                syllables -= 1
            
            syllable_count += syllables
        
        return syllable_count
    
    def _calculate_structure_score(self, heading_hierarchy: Dict[str, int], issues: List[str]) -> float:
        """计算结构评分"""
        score = 1.0
        score -= len(issues) * 0.2
        
        if heading_hierarchy.get('h1', 0) == 1:
            score += 0.2
        
        if heading_hierarchy.get('h2', 0) > 0:
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _calculate_content_quality(self, content: ExtractedContent) -> float:
        """计算内容质量评分"""
        base_score = 0.5
        
        if content.word_count > 300:
            base_score += 0.2
        if content.word_count > 1000:
            base_score += 0.1
        
        if content.schema_org:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _generate_recommendations(self, content: ExtractedContent, seo: SEOAnalysis) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if seo.title_score < 0.8:
            if seo.title_length < 30:
                recommendations.append("Title is too short. Consider expanding to 30-60 characters.")
            elif seo.title_length > 60:
                recommendations.append("Title is too long. Consider shortening to 30-60 characters.")
        
        if seo.meta_description_score < 0.8:
            recommendations.append("Optimize meta description length to 120-160 characters.")
        
        if seo.images_without_alt > 0:
            recommendations.append(f"Add alt text to {seo.images_without_alt} images.")
        
        if not seo.schema_org_present:
            recommendations.append("Consider adding Schema.org structured data.")
        
        return recommendations
