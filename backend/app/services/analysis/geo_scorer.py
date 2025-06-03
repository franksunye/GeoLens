"""
GEO评分算法
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .content_analyzer import AnalysisResult
from .keyword_analyzer import KeywordAnalysis


@dataclass
class GEOFactors:
    """GEO评分因子"""
    content_quality: float
    content_length: float
    readability: float
    originality: float
    title_optimization: float
    meta_description: float
    heading_structure: float
    internal_linking: float
    schema_markup: float
    keyword_relevance: float
    keyword_density: float
    semantic_keywords: float
    page_speed: float
    mobile_friendly: float
    accessibility: float


@dataclass
class GEOScore:
    """GEO评分结果"""
    overall_score: float
    category_scores: Dict[str, float]
    factors: GEOFactors
    recommendations: List[str]
    score_history: List[Dict[str, Any]]
    last_updated: datetime
    
    def get_grade(self) -> str:
        """获取评分等级"""
        if self.overall_score >= 90:
            return "A+"
        elif self.overall_score >= 80:
            return "A"
        elif self.overall_score >= 70:
            return "B"
        elif self.overall_score >= 60:
            return "C"
        elif self.overall_score >= 50:
            return "D"
        else:
            return "F"
    
    def get_visibility_estimate(self) -> str:
        """获取可见性估计"""
        if self.overall_score >= 85:
            return "Excellent - High search visibility expected"
        elif self.overall_score >= 70:
            return "Good - Moderate to high search visibility"
        elif self.overall_score >= 55:
            return "Fair - Limited search visibility"
        elif self.overall_score >= 40:
            return "Poor - Low search visibility"
        else:
            return "Very Poor - Minimal search visibility"


class GEOScorer:
    """GEO评分器"""
    
    def __init__(self):
        self.weights = {
            'content_quality': 0.40,
            'seo_technical': 0.30,
            'keyword_optimization': 0.20,
            'user_experience': 0.10
        }
    
    def calculate_score(
        self,
        content_analysis: AnalysisResult,
        keyword_analysis: KeywordAnalysis,
        url: str = "",
        previous_scores: List[Dict[str, Any]] = None
    ) -> GEOScore:
        """计算GEO评分"""
        
        # 计算各个因子
        factors = self._calculate_factors(content_analysis, keyword_analysis)
        
        # 计算分类评分
        category_scores = self._calculate_category_scores(factors)
        
        # 计算总体评分
        overall_score = self._calculate_overall_score(category_scores)
        
        # 生成建议
        recommendations = self._generate_recommendations(factors, content_analysis)
        
        # 准备历史记录
        score_history = previous_scores or []
        score_history.append({
            'score': overall_score,
            'timestamp': datetime.utcnow().isoformat(),
            'url': url
        })
        
        score_history = score_history[-10:]  # 只保留最近10次记录
        
        return GEOScore(
            overall_score=overall_score,
            category_scores=category_scores,
            factors=factors,
            recommendations=recommendations,
            score_history=score_history,
            last_updated=datetime.utcnow()
        )
    
    def _calculate_factors(
        self,
        content_analysis: AnalysisResult,
        keyword_analysis: KeywordAnalysis
    ) -> GEOFactors:
        """计算各项因子评分"""
        
        # 内容质量因子
        content_quality = content_analysis.content_quality_score
        content_length = self._score_content_length(content_analysis.readability_analysis.word_count)
        readability = content_analysis.readability_analysis.readability_score
        originality = 0.8  # 简化实现
        
        # SEO技术因子
        title_optimization = content_analysis.seo_analysis.title_score
        meta_description = content_analysis.seo_analysis.meta_description_score
        heading_structure = content_analysis.seo_analysis.heading_structure_score
        internal_linking = self._score_internal_linking(content_analysis.seo_analysis.internal_links_count)
        schema_markup = 1.0 if content_analysis.seo_analysis.schema_org_present else 0.0
        
        # 关键词优化因子
        keyword_relevance = keyword_analysis.overall_keyword_score
        keyword_density = self._score_keyword_density(keyword_analysis.target_keywords)
        semantic_keywords = len(keyword_analysis.semantic_keywords) / 10.0  # 简化评分
        
        # 用户体验因子（简化实现）
        page_speed = 0.7
        mobile_friendly = 0.8
        accessibility = 0.7
        
        return GEOFactors(
            content_quality=content_quality,
            content_length=content_length,
            readability=readability,
            originality=originality,
            title_optimization=title_optimization,
            meta_description=meta_description,
            heading_structure=heading_structure,
            internal_linking=internal_linking,
            schema_markup=schema_markup,
            keyword_relevance=keyword_relevance,
            keyword_density=keyword_density,
            semantic_keywords=semantic_keywords,
            page_speed=page_speed,
            mobile_friendly=mobile_friendly,
            accessibility=accessibility
        )
    
    def _calculate_category_scores(self, factors: GEOFactors) -> Dict[str, float]:
        """计算分类评分"""
        
        content_score = (
            factors.content_quality * 0.40 +
            factors.content_length * 0.25 +
            factors.readability * 0.25 +
            factors.originality * 0.10
        ) * 100
        
        seo_score = (
            factors.title_optimization * 0.25 +
            factors.meta_description * 0.20 +
            factors.heading_structure * 0.20 +
            factors.internal_linking * 0.20 +
            factors.schema_markup * 0.15
        ) * 100
        
        keyword_score = (
            factors.keyword_relevance * 0.50 +
            factors.keyword_density * 0.30 +
            factors.semantic_keywords * 0.20
        ) * 100
        
        ux_score = (
            factors.page_speed * 0.40 +
            factors.mobile_friendly * 0.35 +
            factors.accessibility * 0.25
        ) * 100
        
        return {
            'content_quality': content_score,
            'seo_technical': seo_score,
            'keyword_optimization': keyword_score,
            'user_experience': ux_score
        }
    
    def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """计算总体评分"""
        overall_score = (
            category_scores['content_quality'] * self.weights['content_quality'] +
            category_scores['seo_technical'] * self.weights['seo_technical'] +
            category_scores['keyword_optimization'] * self.weights['keyword_optimization'] +
            category_scores['user_experience'] * self.weights['user_experience']
        )
        
        return round(overall_score, 1)
    
    def _score_content_length(self, word_count: int) -> float:
        """评分内容长度"""
        if word_count >= 2000:
            return 1.0
        elif word_count >= 1000:
            return 0.9
        elif word_count >= 500:
            return 0.7
        elif word_count >= 300:
            return 0.5
        else:
            return 0.2
    
    def _score_internal_linking(self, link_count: int) -> float:
        """评分内部链接"""
        if link_count >= 10:
            return 1.0
        elif link_count >= 5:
            return 0.8
        elif link_count >= 2:
            return 0.6
        elif link_count >= 1:
            return 0.4
        else:
            return 0.0
    
    def _score_keyword_density(self, target_keywords: List) -> float:
        """评分关键词密度"""
        if not target_keywords:
            return 0.0
        
        total_score = 0.0
        for keyword in target_keywords:
            density = keyword.density
            if 1.0 <= density <= 3.0:
                score = 1.0
            elif 0.5 <= density < 1.0 or 3.0 < density <= 4.0:
                score = 0.8
            else:
                score = 0.3
            
            total_score += score
        
        return total_score / len(target_keywords)
    
    def _generate_recommendations(
        self,
        factors: GEOFactors,
        content_analysis: AnalysisResult
    ) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if factors.content_quality < 0.7:
            recommendations.append("Improve content quality by adding more valuable information.")
        
        if factors.content_length < 0.7:
            recommendations.append("Increase content length to at least 1000 words.")
        
        if factors.title_optimization < 0.8:
            recommendations.append("Optimize page title length and include target keywords.")
        
        if factors.meta_description < 0.8:
            recommendations.append("Write a compelling meta description between 120-160 characters.")
        
        if factors.schema_markup < 0.5:
            recommendations.append("Add Schema.org structured data for better search understanding.")
        
        return recommendations
