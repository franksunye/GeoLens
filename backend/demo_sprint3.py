#!/usr/bin/env python3
"""
Sprint 3 功能演示脚本

演示内容分析引擎的核心功能：
1. 网页爬虫
2. 内容分析
3. GEO评分
4. 实体提取
5. 关键词分析
"""

import asyncio
import json
from datetime import datetime

# 导入我们的分析模块
from app.services.content_processing import ContentExtractor
from app.services.analysis import ContentAnalyzer, KeywordAnalyzer, GEOScorer, EntityExtractor


async def demo_content_processing():
    """演示内容处理功能"""
    print("📝 演示内容处理功能")
    print("=" * 50)

    # 初始化内容处理器
    content_extractor = ContentExtractor()
    
    # 模拟用户输入的内容（专注GEO分析）
    sample_content = """
    <html>
        <head>
            <title>数字营销策略指南 - 提升SEO效果的完整教程</title>
            <meta name="description" content="学习最新的数字营销策略，包括SEO优化、内容营销和社交媒体推广的实用技巧。">
            <meta name="keywords" content="数字营销,SEO,内容营销,社交媒体">
        </head>
        <body>
            <h1>数字营销策略指南</h1>
            <h2>SEO优化基础</h2>
            <p>搜索引擎优化(SEO)是数字营销的核心组成部分。通过优化网站内容和结构，可以显著提升搜索引擎排名。</p>
            <h2>内容营销策略</h2>
            <p>高质量的内容是吸引用户和搜索引擎的关键。内容营销需要持续创作有价值的内容。</p>
            <h3>关键词研究</h3>
            <p>关键词研究是SEO的基础。选择正确的关键词可以帮助网站获得更多有针对性的流量。</p>
            <h3>技术SEO</h3>
            <p>技术SEO包括网站速度优化、移动端适配、结构化数据等技术层面的优化。</p>
            <a href="https://example.com/seo-guide">SEO完整指南</a>
            <a href="/internal-link">内部链接</a>
            <img src="seo-chart.jpg" alt="SEO效果图表">
            <img src="marketing-funnel.png" alt="">
        </body>
    </html>
    """
    
    # 处理内容
    extracted_content = content_extractor.extract(sample_content, "https://example.com")
    
    print(f"📄 标题: {extracted_content.title}")
    print(f"📝 Meta描述: {extracted_content.meta_description}")
    print(f"🏷️  Meta关键词: {extracted_content.meta_keywords}")
    print(f"📊 单词数: {extracted_content.word_count}")
    print(f"⏱️  阅读时间: {extracted_content.reading_time}分钟")
    print(f"🔗 链接数: {len(extracted_content.links)}")
    print(f"🖼️  图片数: {len(extracted_content.images)}")
    print(f"📋 标题结构: {extracted_content.headings}")
    print()
    
    return extracted_content


def demo_content_analysis(extracted_content):
    """演示内容分析功能"""
    print("📊 演示内容分析功能")
    print("=" * 50)
    
    # 初始化分析器
    content_analyzer = ContentAnalyzer()
    
    # 目标关键词
    target_keywords = ["数字营销", "SEO", "内容营销"]
    
    # 执行分析
    analysis_result = content_analyzer.analyze(extracted_content, target_keywords)
    
    print("🔍 SEO分析结果:")
    seo = analysis_result.seo_analysis
    print(f"  - 标题长度: {seo.title_length} 字符 (评分: {seo.title_score:.2f})")
    print(f"  - Meta描述长度: {seo.meta_description_length} 字符 (评分: {seo.meta_description_score:.2f})")
    print(f"  - 标题结构评分: {seo.heading_structure_score:.2f}")
    print(f"  - 内部链接: {seo.internal_links_count} 个")
    print(f"  - 外部链接: {seo.external_links_count} 个")
    print(f"  - 缺少Alt文本的图片: {seo.images_without_alt} 个")
    print(f"  - Schema.org存在: {seo.schema_org_present}")
    print(f"  - 关键词密度: {seo.keyword_density}")
    print(f"  - SEO总评分: {seo.overall_score():.2f}")
    print()
    
    print("📖 可读性分析结果:")
    readability = analysis_result.readability_analysis
    print(f"  - 单词数: {readability.word_count}")
    print(f"  - 句子数: {readability.sentence_count}")
    print(f"  - 段落数: {readability.paragraph_count}")
    print(f"  - 平均句长: {readability.avg_words_per_sentence:.1f} 词/句")
    print(f"  - Flesch可读性: {readability.flesch_reading_ease:.1f}")
    print(f"  - 阅读难度: {readability.get_reading_level()}")
    print(f"  - 可读性评分: {readability.readability_score:.2f}")
    print()
    
    print("🏗️  结构分析结果:")
    structure = analysis_result.structure_analysis
    print(f"  - 标题层级: {structure.heading_hierarchy}")
    print(f"  - 结构问题: {structure.heading_structure_issues}")
    print(f"  - 内容段落: {structure.content_sections}")
    print(f"  - 结构评分: {structure.structure_score:.2f}")
    print()
    
    print("💡 优化建议:")
    for i, recommendation in enumerate(analysis_result.recommendations, 1):
        print(f"  {i}. {recommendation}")
    print()
    
    print(f"🎯 总体评分: {analysis_result.overall_score():.2f}")
    print()
    
    return analysis_result


def demo_keyword_analysis(extracted_content):
    """演示关键词分析功能"""
    print("🔍 演示关键词分析功能")
    print("=" * 50)
    
    # 初始化关键词分析器
    keyword_analyzer = KeywordAnalyzer()
    
    # 目标关键词
    target_keywords = ["数字营销", "SEO", "内容营销"]
    
    # 执行关键词分析
    keyword_analysis = keyword_analyzer.analyze(
        content=extracted_content.main_content,
        title=extracted_content.title,
        meta_description=extracted_content.meta_description,
        headings=extracted_content.headings,
        target_keywords=target_keywords
    )
    
    print("🎯 目标关键词分析:")
    for keyword in keyword_analysis.target_keywords:
        print(f"  - '{keyword.keyword}':")
        print(f"    频率: {keyword.frequency} 次")
        print(f"    密度: {keyword.density:.2f}%")
        print(f"    突出度: {keyword.prominence_score:.1f}")
        print(f"    相关性: {keyword.context_relevance:.2f}")
    print()
    
    print("🔎 发现的关键词:")
    for keyword in keyword_analysis.discovered_keywords[:5]:  # 显示前5个
        print(f"  - '{keyword.keyword}': {keyword.frequency} 次 (密度: {keyword.density:.2f}%)")
    print()
    
    print(f"⚠️  关键词堆砌风险: {keyword_analysis.keyword_stuffing_risk:.2f}")
    print(f"🎯 关键词总评分: {keyword_analysis.overall_keyword_score:.2f}")
    print()
    
    return keyword_analysis


def demo_entity_extraction(extracted_content):
    """演示实体提取功能"""
    print("🏷️  演示实体提取功能")
    print("=" * 50)
    
    # 初始化实体提取器
    entity_extractor = EntityExtractor()
    
    # 目标品牌
    target_brands = ["Google", "Facebook", "Microsoft"]
    
    # 执行实体提取
    entity_result = entity_extractor.extract(
        extracted_content.main_content,
        target_brands
    )
    
    print(f"👥 人名: {len(entity_result.persons)} 个")
    for person in entity_result.persons:
        print(f"  - {person.text} (置信度: {person.confidence:.2f})")
    
    print(f"🏢 组织: {len(entity_result.organizations)} 个")
    for org in entity_result.organizations:
        print(f"  - {org.text} (置信度: {org.confidence:.2f})")
    
    print(f"🏷️  品牌: {len(entity_result.brands)} 个")
    for brand in entity_result.brands:
        print(f"  - {brand.text} (置信度: {brand.confidence:.2f})")
    
    print(f"💻 技术: {len(entity_result.technologies)} 个")
    for tech in entity_result.technologies:
        print(f"  - {tech.text} (置信度: {tech.confidence:.2f})")
    
    print(f"📊 实体总数: {entity_result.get_entity_count()}")
    print()
    
    return entity_result


def demo_geo_scoring(analysis_result, keyword_analysis):
    """演示GEO评分功能"""
    print("🎯 演示GEO评分功能")
    print("=" * 50)
    
    # 初始化GEO评分器
    geo_scorer = GEOScorer()
    
    # 计算GEO评分
    geo_score = geo_scorer.calculate_score(
        content_analysis=analysis_result,
        keyword_analysis=keyword_analysis,
        url="https://example.com/digital-marketing-guide"
    )
    
    print(f"🏆 总体评分: {geo_score.overall_score:.1f}/100")
    print(f"📊 评分等级: {geo_score.get_grade()}")
    print(f"👁️  可见性预测: {geo_score.get_visibility_estimate()}")
    print()
    
    print("📈 分类评分:")
    for category, score in geo_score.category_scores.items():
        print(f"  - {category}: {score:.1f}/100")
    print()
    
    print("🔧 评分因子:")
    factors = geo_score.factors
    print(f"  - 内容质量: {factors.content_quality:.2f}")
    print(f"  - 内容长度: {factors.content_length:.2f}")
    print(f"  - 可读性: {factors.readability:.2f}")
    print(f"  - 标题优化: {factors.title_optimization:.2f}")
    print(f"  - Meta描述: {factors.meta_description:.2f}")
    print(f"  - 标题结构: {factors.heading_structure:.2f}")
    print(f"  - 内部链接: {factors.internal_linking:.2f}")
    print(f"  - 结构化数据: {factors.schema_markup:.2f}")
    print(f"  - 关键词相关性: {factors.keyword_relevance:.2f}")
    print(f"  - 关键词密度: {factors.keyword_density:.2f}")
    print()
    
    print("💡 优化建议:")
    for i, recommendation in enumerate(geo_score.recommendations, 1):
        print(f"  {i}. {recommendation}")
    print()
    
    return geo_score


# 移除反爬虫演示功能，专注GEO分析


async def main():
    """主演示函数"""
    print("🚀 GeoLens Sprint 3 - 内容分析引擎演示")
    print("=" * 60)
    print(f"⏰ 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. 演示内容处理
        extracted_content = await demo_content_processing()
        
        # 2. 演示内容分析
        analysis_result = demo_content_analysis(extracted_content)
        
        # 3. 演示关键词分析
        keyword_analysis = demo_keyword_analysis(extracted_content)
        
        # 4. 演示实体提取
        entity_result = demo_entity_extraction(extracted_content)
        
        # 5. 演示GEO评分
        geo_score = demo_geo_scoring(analysis_result, keyword_analysis)
        
        # 专注GEO分析，移除反爬虫演示
        
        print("✅ Sprint 3 功能演示完成!")
        print("=" * 60)
        print("🎯 主要功能:")
        print("  ✅ 内容处理系统")
        print("  ✅ GEO分析引擎")
        print("  ✅ 关键词相关性分析")
        print("  ✅ 实体提取")
        print("  ✅ GEO评分算法")
        print("  ✅ AI友好度评估")
        print()
        print("📊 分析结果摘要:")
        print(f"  - GEO评分: {geo_score.overall_score:.1f}/100 ({geo_score.get_grade()})")
        print(f"  - 内容质量: {analysis_result.content_quality_score:.2f}")
        print(f"  - SEO评分: {analysis_result.seo_analysis.overall_score():.2f}")
        print(f"  - 关键词评分: {keyword_analysis.overall_keyword_score:.2f}")
        print(f"  - 实体数量: {entity_result.get_entity_count()}")
        print()
        print("🔮 下一步: Sprint 4 将专注于数据持久化和高级分析功能")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
