"""
关键词分析器
"""

import re
from typing import Dict, List
from dataclasses import dataclass
from collections import Counter


@dataclass
class KeywordMetrics:
    """关键词指标"""
    keyword: str
    frequency: int
    density: float
    prominence_score: float
    positions: List[int]
    context_relevance: float


@dataclass
class KeywordAnalysis:
    """关键词分析结果"""
    target_keywords: List[KeywordMetrics]
    discovered_keywords: List[KeywordMetrics]
    keyword_clusters: Dict[str, List[str]]
    semantic_keywords: List[str]
    keyword_stuffing_risk: float
    overall_keyword_score: float


class KeywordAnalyzer:
    """关键词分析器"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
        
        self.position_weights = {
            'title': 3.0,
            'h1': 2.5,
            'h2': 2.0,
            'meta_description': 2.0,
            'body': 1.0
        }
    
    def analyze(
        self, 
        content: str, 
        title: str = "", 
        meta_description: str = "",
        headings: Dict[str, List[str]] = None,
        target_keywords: List[str] = None
    ) -> KeywordAnalysis:
        """分析关键词"""
        target_keywords = target_keywords or []
        headings = headings or {}
        
        # 准备文本数据
        text_sections = {
            'title': title,
            'meta_description': meta_description,
            'body': content
        }
        
        for level, heading_list in headings.items():
            text_sections[level] = ' '.join(heading_list)
        
        # 分析目标关键词
        target_metrics = self._analyze_target_keywords(target_keywords, text_sections)
        
        # 发现新关键词
        discovered_metrics = self._discover_keywords(text_sections, target_keywords)
        
        # 关键词聚类
        keyword_clusters = {}
        
        # 语义关键词
        semantic_keywords = []
        
        # 关键词堆砌风险
        stuffing_risk = self._calculate_stuffing_risk(target_metrics)
        
        # 总体关键词评分
        overall_score = self._calculate_overall_score(target_metrics)
        
        return KeywordAnalysis(
            target_keywords=target_metrics,
            discovered_keywords=discovered_metrics,
            keyword_clusters=keyword_clusters,
            semantic_keywords=semantic_keywords,
            keyword_stuffing_risk=stuffing_risk,
            overall_keyword_score=overall_score
        )
    
    def _analyze_target_keywords(
        self, 
        target_keywords: List[str], 
        text_sections: Dict[str, str]
    ) -> List[KeywordMetrics]:
        """分析目标关键词"""
        metrics = []
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            frequency = 0
            positions = []
            prominence_score = 0.0
            
            for section_name, text in text_sections.items():
                if not text:
                    continue
                
                text_lower = text.lower()
                count = text_lower.count(keyword_lower)
                frequency += count
                
                weight = self.position_weights.get(section_name, 1.0)
                prominence_score += count * weight
                
                # 记录位置
                start = 0
                while True:
                    pos = text_lower.find(keyword_lower, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1
            
            # 计算密度
            total_words = len(re.findall(r'\b\w+\b', text_sections.get('body', '')))
            density = (frequency / max(total_words, 1)) * 100
            
            # 计算上下文相关性
            context_relevance = 0.5  # 简化实现
            
            metrics.append(KeywordMetrics(
                keyword=keyword,
                frequency=frequency,
                density=density,
                prominence_score=prominence_score,
                positions=positions,
                context_relevance=context_relevance
            ))
        
        return metrics
    
    def _discover_keywords(
        self, 
        text_sections: Dict[str, str], 
        exclude_keywords: List[str]
    ) -> List[KeywordMetrics]:
        """发现新关键词"""
        all_text = ' '.join(text_sections.values())
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # 过滤停用词和已有关键词
        exclude_lower = [k.lower() for k in exclude_keywords]
        filtered_words = [
            w for w in words 
            if w not in self.stop_words and w not in exclude_lower
        ]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        discovered = []
        for word, frequency in word_counts.most_common(10):
            if frequency >= 2:
                total_words = len(words)
                density = (frequency / max(total_words, 1)) * 100
                
                discovered.append(KeywordMetrics(
                    keyword=word,
                    frequency=frequency,
                    density=density,
                    prominence_score=frequency,
                    positions=[],
                    context_relevance=0.5
                ))
        
        return discovered
    
    def _calculate_stuffing_risk(self, target_metrics: List[KeywordMetrics]) -> float:
        """计算关键词堆砌风险"""
        if not target_metrics:
            return 0.0
        
        risk_score = 0.0
        
        for metric in target_metrics:
            if metric.density > 3.0:  # 超过3%认为有风险
                risk_score += (metric.density - 3.0) * 0.1
        
        return min(1.0, risk_score)
    
    def _calculate_overall_score(self, target_metrics: List[KeywordMetrics]) -> float:
        """计算总体关键词评分"""
        if not target_metrics:
            return 0.5
        
        total_score = 0.0
        
        for metric in target_metrics:
            density_score = min(1.0, metric.density / 2.0)  # 2%为最佳密度
            prominence_score = min(1.0, metric.prominence_score / 10.0)
            relevance_score = metric.context_relevance
            
            keyword_score = (density_score * 0.4 + 
                           prominence_score * 0.4 + 
                           relevance_score * 0.2)
            
            total_score += keyword_score
        
        return total_score / len(target_metrics)
