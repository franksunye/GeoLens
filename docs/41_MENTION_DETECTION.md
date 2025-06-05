# 🔍 引用检测技术文档

## 📋 概述

本文档详细介绍GeoLens平台的引用检测 (Mention Detection) 技术实现，包括多模型调用、实体识别算法、引用频率分析等核心技术内容。

## 🎯 什么是引用检测？

**引用检测 (Mention Detection)** 是检测品牌、产品、服务在主流生成式AI（如豆包、DeepSeek、ChatGPT等）中被**生成式回答所提及**的核心技术，提供引用频率、引用上下文与模型来源分析。

### 🔄 引用检测 vs 传统监测

| 维度 | 传统品牌监测 | AI引用检测 |
|------|-------------|-----------|
| **监测对象** | 网页、社交媒体、新闻 | 生成式AI回答内容 |
| **数据来源** | 公开网络内容 | AI模型实时生成内容 |
| **检测方式** | 关键词搜索、爬虫 | 主动提问、实体识别 |
| **评估指标** | 提及次数、情感分析 | 引用频率、推荐概率、上下文质量 |
| **时效性** | 历史数据分析 | 实时AI表现检测 |

## 🏗️ GeoLens的引用检测架构

### 核心技术栈

```
引用检测引擎 = 多模型调用层 + 实体识别层 + 频率分析层 + 可视化层
```

### 1. 多模型调用层

#### 1.1 AI模型集成
- **豆包API**: 字节跳动的生成式AI模型
- **DeepSeek API**: 深度求索的AI模型
- **ChatGPT API**: OpenAI的GPT-4模型
- **统一调用接口**: 标准化的API调用层

#### 1.2 并行处理机制
- **异步调用**: 同时向多个AI模型发送请求
- **超时控制**: 设置合理的响应超时时间
- **错误处理**: 优雅处理API调用失败
- **结果聚合**: 统一处理多模型返回结果

### 2. 实体识别层

#### 2.1 NER + 关键词匹配算法
```python
def detect_brand_mentions(text, brands):
    """
    检测文本中的品牌提及
    准确率目标: ≥95%
    """
    mentions = []
    
    # 1. 预处理文本
    cleaned_text = preprocess_text(text)
    
    # 2. NER实体识别
    entities = ner_model.extract_entities(cleaned_text)
    
    # 3. 关键词精确匹配
    for brand in brands:
        matches = find_exact_matches(cleaned_text, brand)
        mentions.extend(matches)
    
    # 4. 模糊匹配和同义词
    fuzzy_matches = find_fuzzy_matches(cleaned_text, brands)
    mentions.extend(fuzzy_matches)
    
    # 5. 上下文验证
    verified_mentions = verify_context(mentions, cleaned_text)
    
    return verified_mentions
```

#### 2.2 置信度评分
- **精确匹配**: 置信度 0.95-1.00
- **模糊匹配**: 置信度 0.80-0.94
- **上下文推断**: 置信度 0.60-0.79
- **低置信度**: 置信度 < 0.60 (需人工确认)

### 3. 引用频率分析层

#### 3.1 统计算法
```python
def calculate_mention_rate(brand, results):
    """计算品牌引用频率"""
    total_checks = len(results)
    mentioned_count = sum(1 for r in results if brand in r.mentions)
    mention_rate = mentioned_count / total_checks
    
    return {
        'brand': brand,
        'total_checks': total_checks,
        'mentioned_count': mentioned_count,
        'mention_rate': mention_rate,
        'avg_confidence': calculate_avg_confidence(results, brand)
    }
```

#### 3.2 上下文分析
- **位置分析**: 品牌在回答中的位置（第1位、第2位等）
- **推荐强度**: 推荐语气的强弱程度
- **上下文质量**: 提及时的上下文是否正面
- **竞品对比**: 与其他品牌的对比情况

### 4. 可视化层

#### 4.1 数据可视化
- **引用频率图表**: 按品牌/模型显示引用频率
- **趋势分析**: 时间序列的引用变化
- **竞品对比**: 多品牌的对比分析
- **热力图**: 不同场景下的引用表现

#### 4.2 报告生成
- **检测报告**: 详细的检测结果报告
- **趋势报告**: 引用趋势分析报告
- **竞品报告**: 竞品对比分析报告
- **优化建议**: 基于检测结果的优化建议

## 🎯 Prompt模板系统

### 1. 内置模板库

#### 1.1 推荐类模板
```
模板: "推荐几个适合{team_size}人团队使用的{tool_type}工具"
变量: team_size (string), tool_type (string)
场景: 工具推荐、产品对比
```

#### 1.2 对比类模板
```
模板: "对比{brand1}和{brand2}这两个{category}的优缺点"
变量: brand1 (string), brand2 (string), category (string)
场景: 竞品对比、功能分析
```

#### 1.3 问题解决类模板
```
模板: "如何选择合适的{solution_type}来解决{problem}问题？"
变量: solution_type (string), problem (string)
场景: 解决方案推荐、问题咨询
```

### 2. 自定义模板

#### 2.1 模板创建
- **模板编辑器**: 可视化的模板创建界面
- **变量定义**: 支持多种变量类型
- **预览功能**: 实时预览模板效果
- **模板验证**: 检查模板的有效性

#### 2.2 模板管理
- **分类管理**: 按行业、场景分类
- **使用统计**: 跟踪模板使用频率
- **效果评估**: 评估模板的检测效果
- **共享机制**: 支持模板分享和复用

## 📊 检测精度优化

### 1. 准确率提升策略

#### 1.1 多层验证机制
```python
def multi_layer_verification(text, brand, initial_confidence):
    """多层验证提升准确率"""
    
    # 第一层: 精确匹配验证
    exact_match = verify_exact_match(text, brand)
    if exact_match:
        return min(initial_confidence + 0.1, 1.0)
    
    # 第二层: 上下文语义验证
    context_score = verify_semantic_context(text, brand)
    
    # 第三层: 同义词和变体验证
    variant_score = verify_brand_variants(text, brand)
    
    # 综合评分
    final_confidence = (initial_confidence + context_score + variant_score) / 3
    return final_confidence
```

#### 1.2 误报减少技术
- **否定词检测**: 识别"不推荐"、"避免使用"等否定表达
- **上下文过滤**: 过滤无关上下文中的品牌提及
- **同名过滤**: 区分同名但不同类别的品牌
- **语言模型验证**: 使用语言模型验证提及的合理性

### 2. 性能优化

#### 2.1 响应时间优化
- **并行处理**: 多模型并行调用
- **缓存机制**: 缓存常见查询结果
- **批量处理**: 支持批量检测请求
- **异步队列**: 大量请求的异步处理

#### 2.2 成本控制
- **智能调度**: 根据模型成本和性能选择
- **请求优化**: 减少不必要的API调用
- **结果复用**: 复用相似查询的结果
- **预算控制**: 设置API调用预算限制

## 🔮 技术发展路线

### 1. 短期优化 (1-3个月)
- **检测精度提升**: 目标准确率达到98%
- **响应速度优化**: 单次检测时间<5秒
- **模型扩展**: 支持更多AI模型
- **批量处理**: 支持批量检测功能

### 2. 中期发展 (3-6个月)
- **智能分析**: AI驱动的上下文质量分析
- **趋势预测**: 基于历史数据的趋势预测
- **自动优化**: 自动生成优化建议
- **多语言支持**: 支持多语言检测

### 3. 长期规划 (6-12个月)
- **多模态检测**: 支持图像、视频中的品牌检测
- **实时监控**: 7x24小时实时监控
- **预警系统**: 品牌提及异常预警
- **生态集成**: 与营销工具深度集成

---

**引用检测技术是AI时代品牌监测的核心，GeoLens致力于成为这个领域的技术领导者！**

*文档版本: v2.0*  
*最后更新: 2024-06-03*
