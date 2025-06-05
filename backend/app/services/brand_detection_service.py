"""
品牌检测服务
提供统一的品牌检测接口和多种检测策略
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from app.services.base import BaseService
from app.services.brand_detection import ImprovedBrandDetector


class DetectionStrategy(str, Enum):
    """检测策略"""
    SIMPLE = "simple"           # 简单字符串匹配
    IMPROVED = "improved"       # 改进的检测算法
    ML_BASED = "ml_based"      # 基于机器学习（未来）
    HYBRID = "hybrid"          # 混合策略


@dataclass
class BrandDetectionResult:
    """品牌检测结果"""
    brand: str
    mentioned: bool
    confidence: float
    contexts: List[str]
    positions: List[int]
    detection_method: str
    metadata: Optional[Dict[str, Any]] = None


class BrandDetector(ABC):
    """品牌检测器抽象基类"""
    
    @abstractmethod
    def detect(self, text: str, brands: List[str]) -> Dict[str, BrandDetectionResult]:
        """检测品牌提及"""
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """策略名称"""
        pass


class SimpleBrandDetector(BrandDetector):
    """简单品牌检测器"""
    
    def detect(self, text: str, brands: List[str]) -> Dict[str, BrandDetectionResult]:
        """简单字符串匹配检测"""
        results = {}
        text_lower = text.lower()
        
        for brand in brands:
            brand_lower = brand.lower()
            mentioned = brand_lower in text_lower
            
            if mentioned:
                pos = text_lower.find(brand_lower)
                context = text[max(0, pos-50):min(len(text), pos+len(brand)+50)]
                
                results[brand] = BrandDetectionResult(
                    brand=brand,
                    mentioned=True,
                    confidence=0.8,
                    contexts=[context],
                    positions=[pos],
                    detection_method="simple_match"
                )
            else:
                results[brand] = BrandDetectionResult(
                    brand=brand,
                    mentioned=False,
                    confidence=0.0,
                    contexts=[],
                    positions=[],
                    detection_method="simple_match"
                )
        
        return results
    
    @property
    def strategy_name(self) -> str:
        return "simple"


class ImprovedBrandDetectorWrapper(BrandDetector):
    """改进品牌检测器包装器"""
    
    def __init__(self):
        self.detector = ImprovedBrandDetector()
    
    def detect(self, text: str, brands: List[str]) -> Dict[str, BrandDetectionResult]:
        """使用改进的检测算法"""
        mentions = self.detector.detect_brand_mentions(text, brands)
        
        results = {}
        for brand, mention in mentions.items():
            results[brand] = BrandDetectionResult(
                brand=brand,
                mentioned=mention.mentioned,
                confidence=mention.confidence,
                contexts=mention.contexts,
                positions=mention.positions,
                detection_method=mention.mention_type,
                metadata={
                    "mention_count": len(mention.positions),
                    "avg_context_length": sum(len(c) for c in mention.contexts) / len(mention.contexts) if mention.contexts else 0
                }
            )
        
        return results
    
    @property
    def strategy_name(self) -> str:
        return "improved"


class HybridBrandDetector(BrandDetector):
    """混合品牌检测器"""
    
    def __init__(self):
        self.simple_detector = SimpleBrandDetector()
        self.improved_detector = ImprovedBrandDetectorWrapper()
    
    def detect(self, text: str, brands: List[str]) -> Dict[str, BrandDetectionResult]:
        """使用多种策略进行检测并合并结果"""
        simple_results = self.simple_detector.detect(text, brands)
        improved_results = self.improved_detector.detect(text, brands)
        
        # 合并结果，优先使用改进算法的结果
        final_results = {}
        for brand in brands:
            improved_result = improved_results[brand]
            simple_result = simple_results[brand]
            
            # 如果改进算法检测到提及，使用改进算法结果
            if improved_result.mentioned:
                final_results[brand] = improved_result
            # 如果改进算法未检测到但简单算法检测到，使用简单算法结果但降低置信度
            elif simple_result.mentioned:
                final_results[brand] = BrandDetectionResult(
                    brand=brand,
                    mentioned=True,
                    confidence=simple_result.confidence * 0.7,  # 降低置信度
                    contexts=simple_result.contexts,
                    positions=simple_result.positions,
                    detection_method="hybrid_fallback"
                )
            else:
                final_results[brand] = improved_result
        
        return final_results
    
    @property
    def strategy_name(self) -> str:
        return "hybrid"


class BrandDetectionService(BaseService):
    """品牌检测服务"""
    
    def __init__(self, db=None):
        super().__init__(db)
        self._detectors = {
            DetectionStrategy.SIMPLE: SimpleBrandDetector(),
            DetectionStrategy.IMPROVED: ImprovedBrandDetectorWrapper(),
            DetectionStrategy.HYBRID: HybridBrandDetector()
        }
        self._default_strategy = DetectionStrategy.IMPROVED
    
    def set_default_strategy(self, strategy: DetectionStrategy):
        """设置默认检测策略"""
        self._default_strategy = strategy
    
    def detect_brands(
        self,
        text: str,
        brands: List[str],
        strategy: Optional[DetectionStrategy] = None
    ) -> Dict[str, BrandDetectionResult]:
        """
        检测品牌提及
        
        Args:
            text: 要检测的文本
            brands: 品牌列表
            strategy: 检测策略
            
        Returns:
            品牌检测结果
        """
        if strategy is None:
            strategy = self._default_strategy
        
        if strategy not in self._detectors:
            raise ValueError(f"Unsupported detection strategy: {strategy}")
        
        detector = self._detectors[strategy]
        return detector.detect(text, brands)
    
    def compare_strategies(
        self,
        text: str,
        brands: List[str],
        strategies: Optional[List[DetectionStrategy]] = None
    ) -> Dict[str, Dict[str, BrandDetectionResult]]:
        """
        比较不同检测策略的结果
        
        Args:
            text: 要检测的文本
            brands: 品牌列表
            strategies: 要比较的策略列表
            
        Returns:
            各策略的检测结果
        """
        if strategies is None:
            strategies = [DetectionStrategy.SIMPLE, DetectionStrategy.IMPROVED]
        
        results = {}
        for strategy in strategies:
            if strategy in self._detectors:
                detector = self._detectors[strategy]
                results[strategy.value] = detector.detect(text, brands)
        
        return results
    
    def get_detection_statistics(
        self,
        results: Dict[str, BrandDetectionResult]
    ) -> Dict[str, Any]:
        """
        获取检测统计信息
        
        Args:
            results: 检测结果
            
        Returns:
            统计信息
        """
        total_brands = len(results)
        mentioned_brands = sum(1 for r in results.values() if r.mentioned)
        avg_confidence = sum(r.confidence for r in results.values()) / total_brands if total_brands > 0 else 0
        
        detection_methods = {}
        for result in results.values():
            method = result.detection_method
            detection_methods[method] = detection_methods.get(method, 0) + 1
        
        return {
            "total_brands": total_brands,
            "mentioned_brands": mentioned_brands,
            "mention_rate": mentioned_brands / total_brands if total_brands > 0 else 0,
            "avg_confidence": round(avg_confidence, 4),
            "detection_methods": detection_methods
        }
    
    def register_detector(self, strategy: DetectionStrategy, detector: BrandDetector):
        """注册新的检测器"""
        self._detectors[strategy] = detector
    
    def get_available_strategies(self) -> List[str]:
        """获取可用的检测策略"""
        return [strategy.value for strategy in self._detectors.keys()]


# 便捷函数
def quick_brand_detection(
    text: str,
    brands: List[str],
    strategy: DetectionStrategy = DetectionStrategy.IMPROVED
) -> Dict[str, BrandDetectionResult]:
    """快速品牌检测"""
    service = BrandDetectionService()
    return service.detect_brands(text, brands, strategy)
