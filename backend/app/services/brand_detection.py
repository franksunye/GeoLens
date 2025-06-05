"""
改进的品牌检测服务
解决端到端测试中发现的品牌检测准确性问题
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BrandMention:
    """品牌提及结果"""
    brand: str
    mentioned: bool
    confidence: float
    positions: List[int]
    contexts: List[str]
    mention_type: str  # 'exact', 'variant', 'implicit'


class ImprovedBrandDetector:
    """改进的品牌检测器"""
    
    def __init__(self):
        # 品牌名称变体映射
        self.brand_variants = {
            "Notion": [
                "notion", "notion.so", "notion app", "notion软件",
                "notion笔记", "notion工具", "notion平台"
            ],
            "Obsidian": [
                "obsidian", "obsidian.md", "obsidian笔记", "obsidian软件",
                "黑曜石", "obsidian工具", "obsidian应用"
            ],
            "Roam Research": [
                "roam research", "roam", "roamresearch", "roam笔记",
                "roam research软件", "roam工具", "roam应用"
            ],
            "Confluence": [
                "confluence", "atlassian confluence", "confluence软件",
                "confluence工具", "confluence平台", "atlassian"
            ],
            "Logseq": [
                "logseq", "logseq笔记", "logseq软件", "logseq工具", "logseq应用"
            ],
            "RemNote": [
                "remnote", "rem note", "remnote笔记", "remnote软件", "remnote应用"
            ],
            "Evernote": [
                "evernote", "印象笔记", "evernote软件", "evernote工具", "evernote应用"
            ],
            "OneNote": [
                "onenote", "one note", "microsoft onenote", "onenote笔记", "微软笔记"
            ]
        }
        
        # 隐式提及模式（通过功能描述推断品牌）
        self.implicit_patterns = {
            "Notion": [
                r"数据库.*笔记", r"块.*编辑", r"模板.*页面", r"协作.*工作区",
                r"all-in-one.*工作空间", r"页面.*数据库.*模板"
            ],
            "Obsidian": [
                r"双向链接.*笔记", r"知识图谱", r"markdown.*本地", r"插件.*扩展",
                r"本地.*存储.*笔记", r"图谱.*可视化"
            ],
            "Roam Research": [
                r"双向链接.*研究", r"块.*引用", r"每日笔记.*时间戳",
                r"网状.*思维", r"关联.*思考"
            ]
        }
    
    def detect_brand_mentions(self, text: str, target_brands: List[str]) -> Dict[str, BrandMention]:
        """
        检测文本中的品牌提及
        
        Args:
            text: 要检测的文本
            target_brands: 目标品牌列表
            
        Returns:
            品牌提及结果字典
        """
        results = {}
        text_lower = text.lower()
        
        for brand in target_brands:
            mention = self._detect_single_brand(text, text_lower, brand)
            results[brand] = mention
        
        return results
    
    def _detect_single_brand(self, original_text: str, text_lower: str, brand: str) -> BrandMention:
        """检测单个品牌的提及"""
        positions = []
        contexts = []
        mention_types = []
        
        # 1. 精确匹配
        exact_positions = self._find_exact_matches(text_lower, brand)
        if exact_positions:
            positions.extend(exact_positions)
            mention_types.append('exact')
            contexts.extend(self._extract_contexts(original_text, exact_positions, brand))
        
        # 2. 变体匹配
        if brand in self.brand_variants:
            for variant in self.brand_variants[brand]:
                variant_positions = self._find_exact_matches(text_lower, variant)
                if variant_positions:
                    positions.extend(variant_positions)
                    mention_types.append('variant')
                    contexts.extend(self._extract_contexts(original_text, variant_positions, variant))
        
        # 3. 隐式匹配（通过功能描述）
        if brand in self.implicit_patterns:
            implicit_matches = self._find_implicit_matches(text_lower, brand)
            if implicit_matches:
                mention_types.append('implicit')
                contexts.extend(implicit_matches)
        
        # 计算置信度
        confidence = self._calculate_confidence(positions, mention_types, contexts)
        
        # 去重和排序
        positions = sorted(list(set(positions)))
        contexts = list(set(contexts))
        
        return BrandMention(
            brand=brand,
            mentioned=len(positions) > 0 or len(contexts) > 0,
            confidence=confidence,
            positions=positions,
            contexts=contexts,
            mention_type=','.join(set(mention_types)) if mention_types else 'none'
        )
    
    def _find_exact_matches(self, text_lower: str, search_term: str) -> List[int]:
        """查找精确匹配的位置"""
        positions = []
        search_lower = search_term.lower()
        start = 0

        while True:
            pos = text_lower.find(search_lower, start)
            if pos == -1:
                break

            # 对于中英文混合的品牌名，放宽边界检查
            if len(search_lower) <= 3 or self._is_word_boundary(text_lower, pos, len(search_lower)):
                positions.append(pos)

            start = pos + 1

        return positions
    
    def _is_word_boundary(self, text: str, start: int, length: int) -> bool:
        """检查是否为完整单词边界"""
        # 检查前面的字符
        if start > 0:
            prev_char = text[start - 1]
            # 放宽对中文字符的限制
            if prev_char.isalnum() and ord(prev_char) < 128:  # 只对ASCII字符严格检查
                return False

        # 检查后面的字符
        end = start + length
        if end < len(text):
            next_char = text[end]
            # 放宽对中文字符的限制
            if next_char.isalnum() and ord(next_char) < 128:  # 只对ASCII字符严格检查
                return False

        return True
    
    def _find_implicit_matches(self, text_lower: str, brand: str) -> List[str]:
        """查找隐式匹配"""
        matches = []
        
        if brand not in self.implicit_patterns:
            return matches
        
        for pattern in self.implicit_patterns[brand]:
            if re.search(pattern, text_lower):
                # 提取匹配的上下文
                match = re.search(pattern, text_lower)
                if match:
                    start = max(0, match.start() - 20)
                    end = min(len(text_lower), match.end() + 20)
                    context = text_lower[start:end].strip()
                    matches.append(f"隐式匹配: {context}")
        
        return matches
    
    def _extract_contexts(self, text: str, positions: List[int], search_term: str) -> List[str]:
        """提取上下文"""
        contexts = []
        
        for pos in positions:
            # 提取前后各50个字符作为上下文
            start = max(0, pos - 50)
            end = min(len(text), pos + len(search_term) + 50)
            context = text[start:end].strip()
            
            # 清理上下文
            context = re.sub(r'\s+', ' ', context)
            contexts.append(context)
        
        return contexts
    
    def _calculate_confidence(self, positions: List[int], mention_types: List[str], contexts: List[str]) -> float:
        """计算置信度"""
        if not positions and not contexts:
            return 0.0
        
        confidence = 0.0
        
        # 基础分数
        if positions:
            confidence += 0.6  # 有明确位置匹配
        
        # 根据提及类型调整
        if 'exact' in mention_types:
            confidence += 0.3
        elif 'variant' in mention_types:
            confidence += 0.2
        elif 'implicit' in mention_types:
            confidence += 0.1
        
        # 根据提及次数调整
        mention_count = len(positions) + len([c for c in contexts if '隐式匹配' in c])
        if mention_count > 1:
            confidence += min(0.2, mention_count * 0.05)
        
        # 根据上下文质量调整
        if contexts:
            avg_context_length = sum(len(c) for c in contexts) / len(contexts)
            if avg_context_length > 30:  # 有足够的上下文
                confidence += 0.1
        
        return min(1.0, confidence)


def analyze_brand_mentions(text: str, brands: List[str]) -> Dict[str, Dict]:
    """
    分析文本中的品牌提及（兼容现有接口）
    
    Args:
        text: 要分析的文本
        brands: 品牌列表
        
    Returns:
        品牌分析结果
    """
    detector = ImprovedBrandDetector()
    mentions = detector.detect_brand_mentions(text, brands)
    
    # 转换为兼容格式
    results = {}
    for brand, mention in mentions.items():
        results[brand] = {
            'mentioned': mention.mentioned,
            'confidence': mention.confidence,
            'mention_count': len(mention.positions),
            'contexts': mention.contexts,
            'mention_type': mention.mention_type,
            'positions': mention.positions
        }
    
    return results


# 测试函数
def test_brand_detection():
    """测试品牌检测功能"""
    test_cases = [
        {
            'text': '推荐几个好用的笔记软件，比如Notion和Obsidian都很不错',
            'brands': ['Notion', 'Obsidian', 'Roam Research'],
            'expected': {'Notion': True, 'Obsidian': True, 'Roam Research': False}
        },
        {
            'text': '印象笔记是一个功能全面的笔记软件，支持多平台同步',
            'brands': ['Notion', 'Evernote'],
            'expected': {'Notion': False, 'Evernote': True}
        },
        {
            'text': '我需要一个支持双向链接和知识图谱的笔记工具',
            'brands': ['Notion', 'Obsidian', 'Roam Research'],
            'expected': {'Notion': False, 'Obsidian': True, 'Roam Research': True}
        }
    ]
    
    detector = ImprovedBrandDetector()
    
    for i, case in enumerate(test_cases):
        print(f"\n测试案例 {i+1}: {case['text']}")
        results = detector.detect_brand_mentions(case['text'], case['brands'])
        
        for brand in case['brands']:
            expected = case['expected'][brand]
            actual = results[brand].mentioned
            status = "✅" if expected == actual else "❌"
            
            print(f"  {status} {brand}: 预期={expected}, 实际={actual}, 置信度={results[brand].confidence:.2f}")
            if results[brand].contexts:
                print(f"      上下文: {results[brand].contexts[0][:50]}...")


if __name__ == "__main__":
    test_brand_detection()
