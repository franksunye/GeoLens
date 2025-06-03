# 📊 内容分析引擎技术文档

## 概述

内容分析引擎是GeoLens平台的核心组件，提供全面的网页内容分析、SEO评估和GEO评分功能。该引擎采用模块化设计，支持异步处理，具备高性能和可扩展性。

## 🏗️ 架构设计

### 核心模块

```
app/services/
├── crawler/                 # 网页爬虫模块
│   ├── base.py             # 抽象基类和数据结构
│   ├── html_crawler.py     # HTML爬虫实现
│   ├── content_extractor.py # 内容提取器
│   └── anti_bot.py         # 反爬虫策略
└── analysis/               # 内容分析模块
    ├── content_analyzer.py  # 内容综合分析
    ├── keyword_analyzer.py  # 关键词分析
    ├── entity_extractor.py  # 实体提取
    └── geo_scorer.py       # GEO评分算法
```

### 数据流

```
URL输入 → 网页爬取 → 内容提取 → 多维度分析 → GEO评分 → 优化建议
```

## 🕷️ 网页爬虫系统

### HTMLCrawler

异步HTML爬虫，支持：
- 重试机制（指数退避）
- 反爬虫策略
- 批量处理
- 错误分类处理

```python
crawler = HTMLCrawler(
    timeout=30,
    max_retries=3,
    follow_redirects=True
)

result = await crawler.crawl("https://example.com")
```

### ContentExtractor

智能内容提取器，提取：
- 页面标题和Meta信息
- 主要内容文本
- 标题层级结构
- 链接和图片
- Schema.org结构化数据

### AntiBot

反爬虫策略处理：
- 用户代理轮换（桌面端/移动端）
- 请求频率控制
- 域名状态管理
- 反爬虫措施检测

## 📊 内容分析引擎

### ContentAnalyzer

综合内容分析器，提供三大分析维度：

#### 1. SEO分析
- **标题优化**: 长度评分（30-60字符最佳）
- **Meta描述**: 长度评分（120-160字符最佳）
- **标题结构**: H1唯一性、层级合理性
- **Schema.org**: 结构化数据检测
- **图片优化**: Alt文本完整性

#### 2. 可读性分析
- **Flesch Reading Ease**: 标准可读性评分算法
- **句子分析**: 平均句长、句子数量
- **段落分析**: 段落数量、平均句数
- **阅读时间**: 基于200词/分钟估算

#### 3. 结构分析
- **标题层级**: H1-H6分布统计
- **内容组织**: 段落、列表、表格检测
- **结构问题**: 缺失H1、多个H1、层级跳跃

### KeywordAnalyzer

关键词分析系统：

#### 目标关键词分析
- **频率统计**: 关键词出现次数
- **密度计算**: 关键词密度百分比
- **位置权重**: 标题(3.0) > H1(2.5) > H2(2.0) > Meta(2.0) > 正文(1.0)
- **上下文相关性**: 关键词与周围内容的相关度

#### 关键词发现
- **自动发现**: 基于词频的新关键词识别
- **停用词过滤**: 移除无意义词汇
- **词根聚类**: 相似词汇分组

#### 风险检测
- **堆砌检测**: 关键词密度过高风险评估
- **分布分析**: 关键词在页面中的分布

### EntityExtractor

实体提取系统：

#### 支持的实体类型
- **人名**: 基于模式的人名识别
- **组织**: 公司、机构名称（含后缀识别）
- **品牌**: 已知品牌和目标品牌
- **技术**: 编程语言、技术栈
- **其他**: 邮箱、URL、电话等

#### 提取算法
- **正则表达式**: 基于模式的实体匹配
- **词典匹配**: 预定义实体库匹配
- **置信度评分**: 基于匹配质量的可信度
- **去重处理**: 大小写不敏感的重复实体合并

## 🎯 GEO评分算法

### 评分模型

四维度加权评分模型：

```
GEO评分 = 内容质量(40%) + SEO技术(30%) + 关键词优化(20%) + 用户体验(10%)
```

#### 1. 内容质量 (40%)
- **内容质量**: 基础内容评估
- **内容长度**: 字数评分（2000+词最佳）
- **可读性**: Flesch评分转换
- **原创性**: 内容原创度评估

#### 2. SEO技术 (30%)
- **标题优化**: 标题长度和关键词
- **Meta描述**: 描述质量和长度
- **标题结构**: H1-H6层级合理性
- **内部链接**: 内链数量和质量
- **结构化数据**: Schema.org标记

#### 3. 关键词优化 (20%)
- **关键词相关性**: 目标关键词匹配度
- **关键词密度**: 密度合理性（1-3%最佳）
- **语义关键词**: 相关词汇丰富度

#### 4. 用户体验 (10%)
- **页面速度**: 加载速度评估
- **移动友好**: 移动端适配
- **可访问性**: 无障碍访问支持

### 评分等级

| 分数范围 | 等级 | 可见性预测 |
|---------|------|-----------|
| 90-100  | A+   | 优秀 - 高搜索可见性 |
| 80-89   | A    | 良好 - 中高搜索可见性 |
| 70-79   | B    | 一般 - 中等搜索可见性 |
| 60-69   | C    | 较差 - 有限搜索可见性 |
| 50-59   | D    | 差 - 低搜索可见性 |
| 0-49    | F    | 很差 - 极低搜索可见性 |

## 🌐 API接口

### 健康检查
```http
GET /api/v1/analysis/health
```

### 内容分析
```http
POST /api/v1/analysis/analyze
Content-Type: application/json

{
  "url": "https://example.com",
  "target_keywords": ["SEO", "内容营销"],
  "brand_keywords": ["品牌名"]
}
```

### GEO评分
```http
POST /api/v1/analysis/geo-score
Content-Type: application/json

{
  "url": "https://example.com",
  "target_keywords": ["SEO", "内容营销"]
}
```

## 🧪 测试策略

### 测试覆盖率
- **总体覆盖率**: 87%
- **爬虫模块**: 92%
- **分析模块**: 89%

### 测试类型
- **单元测试**: 各模块功能测试
- **集成测试**: API端点测试
- **性能测试**: 爬虫和分析性能
- **算法测试**: 评分算法准确性

## 🚀 性能优化

### 异步处理
- 全异步爬虫系统
- 并发控制和资源管理
- 批量处理优化

### 缓存策略
- 爬取结果缓存
- 分析结果缓存
- 反爬虫状态缓存

### 错误处理
- 分层错误处理
- 重试机制
- 降级策略

## 🔮 扩展性

### 算法扩展
- 新增分析维度
- 自定义评分权重
- 机器学习模型集成

### 数据源扩展
- 多种内容格式支持
- 社交媒体内容分析
- 多语言内容支持

### 集成扩展
- 第三方SEO工具集成
- 分析结果导出
- 实时监控功能

## 📝 使用示例

### 完整分析流程

```python
from app.services.crawler import HTMLCrawler, ContentExtractor
from app.services.analysis import ContentAnalyzer, KeywordAnalyzer, GEOScorer

# 1. 爬取网页
crawler = HTMLCrawler()
crawl_result = await crawler.crawl("https://example.com")

# 2. 提取内容
extractor = ContentExtractor()
content = extractor.extract(crawl_result.content)

# 3. 内容分析
analyzer = ContentAnalyzer()
content_analysis = analyzer.analyze(content, ["SEO", "内容营销"])

# 4. 关键词分析
keyword_analyzer = KeywordAnalyzer()
keyword_analysis = keyword_analyzer.analyze(
    content.main_content, 
    content.title,
    target_keywords=["SEO", "内容营销"]
)

# 5. GEO评分
scorer = GEOScorer()
geo_score = scorer.calculate_score(content_analysis, keyword_analysis)

print(f"GEO评分: {geo_score.overall_score}/100 ({geo_score.get_grade()})")
```

## 🛠️ 配置选项

### 爬虫配置
```python
crawler = HTMLCrawler(
    timeout=30,              # 请求超时时间
    max_retries=3,           # 最大重试次数
    retry_delay=1.0,         # 重试延迟
    follow_redirects=True,   # 跟随重定向
    max_content_size=10*1024*1024  # 最大内容大小
)
```

### 分析配置
```python
scorer = GEOScorer()
scorer.weights = {
    'content_quality': 0.40,     # 内容质量权重
    'seo_technical': 0.30,       # SEO技术权重
    'keyword_optimization': 0.20, # 关键词优化权重
    'user_experience': 0.10      # 用户体验权重
}
```

---

*文档版本: v0.3.0-sprint3*  
*最后更新: 2024-06-03*
