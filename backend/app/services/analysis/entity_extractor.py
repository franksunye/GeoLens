"""
实体提取器
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Entity:
    """实体数据结构"""
    text: str
    entity_type: str
    confidence: float
    positions: List[int]
    context: List[str]


@dataclass
class EntityResult:
    """实体提取结果"""
    persons: List[Entity]
    organizations: List[Entity]
    locations: List[Entity]
    brands: List[Entity]
    products: List[Entity]
    technologies: List[Entity]
    other: List[Entity]
    
    def get_all_entities(self) -> List[Entity]:
        """获取所有实体"""
        return (self.persons + self.organizations + self.locations + 
                self.brands + self.products + self.technologies + self.other)
    
    def get_entity_count(self) -> int:
        """获取实体总数"""
        return len(self.get_all_entities())


class EntityExtractor:
    """实体提取器"""
    
    def __init__(self):
        self.org_suffixes = {
            'inc', 'corp', 'corporation', 'company', 'co', 'ltd', 'limited',
            'llc', 'group', 'tech', 'software', 'services'
        }
        
        self.tech_keywords = {
            'ai', 'artificial intelligence', 'machine learning', 'python', 'javascript',
            'react', 'vue', 'angular', 'node.js', 'docker', 'kubernetes'
        }
        
        self.known_brands = {
            'apple', 'google', 'microsoft', 'amazon', 'facebook', 'meta',
            'tesla', 'netflix', 'spotify', 'uber', 'twitter', 'instagram'
        }
    
    def extract(self, text: str, target_brands: List[str] = None) -> EntityResult:
        """提取实体"""
        if not text:
            return EntityResult([], [], [], [], [], [], [])
        
        text = self._preprocess_text(text)
        
        persons = self._extract_persons(text)
        organizations = self._extract_organizations(text)
        locations = []  # 简化实现
        brands = self._extract_brands(text, target_brands or [])
        products = []  # 简化实现
        technologies = self._extract_technologies(text)
        other = []  # 简化实现
        
        return EntityResult(
            persons=persons,
            organizations=organizations,
            locations=locations,
            brands=brands,
            products=products,
            technologies=technologies,
            other=other
        )
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_persons(self, text: str) -> List[Entity]:
        """提取人名"""
        persons = []
        
        # 简单的人名模式：首字母大写的连续单词
        person_pattern = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b')
        
        for match in person_pattern.finditer(text):
            name = match.group()
            
            if self._is_likely_person_name(name):
                entity = Entity(
                    text=name,
                    entity_type='PERSON',
                    confidence=0.7,
                    positions=[match.start()],
                    context=[self._get_context(text, match.start(), match.end())]
                )
                persons.append(entity)
        
        return self._deduplicate_entities(persons)
    
    def _extract_organizations(self, text: str) -> List[Entity]:
        """提取组织名"""
        organizations = []
        
        # 查找包含组织后缀的实体
        for suffix in self.org_suffixes:
            pattern = re.compile(rf'\b[A-Z][A-Za-z\s]+\s+{suffix}\b', re.IGNORECASE)
            
            for match in pattern.finditer(text):
                org_name = match.group().strip()
                
                entity = Entity(
                    text=org_name,
                    entity_type='ORGANIZATION',
                    confidence=0.8,
                    positions=[match.start()],
                    context=[self._get_context(text, match.start(), match.end())]
                )
                organizations.append(entity)
        
        return self._deduplicate_entities(organizations)
    
    def _extract_brands(self, text: str, target_brands: List[str]) -> List[Entity]:
        """提取品牌名"""
        brands = []
        
        # 合并已知品牌和目标品牌
        all_brands = set(self.known_brands)
        all_brands.update([brand.lower() for brand in target_brands])
        
        for brand in all_brands:
            pattern = re.compile(rf'\b{re.escape(brand)}\b', re.IGNORECASE)
            
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    entity_type='BRAND',
                    confidence=0.9 if brand in [b.lower() for b in target_brands] else 0.7,
                    positions=[match.start()],
                    context=[self._get_context(text, match.start(), match.end())]
                )
                brands.append(entity)
        
        return self._deduplicate_entities(brands)
    
    def _extract_technologies(self, text: str) -> List[Entity]:
        """提取技术名词"""
        technologies = []
        
        for tech in self.tech_keywords:
            pattern = re.compile(rf'\b{re.escape(tech)}\b', re.IGNORECASE)
            
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    entity_type='TECHNOLOGY',
                    confidence=0.8,
                    positions=[match.start()],
                    context=[self._get_context(text, match.start(), match.end())]
                )
                technologies.append(entity)
        
        return self._deduplicate_entities(technologies)
    
    def _is_likely_person_name(self, name: str) -> bool:
        """判断是否可能是人名"""
        words = name.split()
        
        # 人名通常是2-4个单词
        if len(words) < 2 or len(words) > 4:
            return False
        
        # 检查是否包含常见的非人名词汇
        non_person_words = {'the', 'and', 'or', 'of', 'in', 'on', 'at'}
        if any(word.lower() in non_person_words for word in words):
            return False
        
        return True
    
    def _get_context(self, text: str, start: int, end: int, window: int = 30) -> str:
        """获取实体的上下文"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """去重实体"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.text.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
