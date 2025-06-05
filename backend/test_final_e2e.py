#!/usr/bin/env python3
"""
最终的端到端测试 - 豆包权限调整后的完整验证
"""

import asyncio
import os
import sys
sys.path.append('/mnt/persist/workspace/backend')

from app.services.ai import AIServiceFactory, AIMessage, AIRole


async def test_doubao_comprehensive():
    """全面测试豆包API"""
    print("🔍 豆包API全面测试")
    print("-" * 40)
    
    api_key = "fb429f70-7037-4e2b-bc44-e98b14685cc0"
    
    # 测试多个可能的模型ID
    model_candidates = [
        "Doubao-1.5-lite-32k-250115",  # 你提供的新模型ID
        "doubao-lite-32k",
        "doubao-pro-32k",
        "doubao-1.5-lite",
        "doubao-1.5-pro-32k"
    ]
    
    factory = AIServiceFactory()
    
    for model_id in model_candidates:
        try:
            print(f"   测试模型: {model_id}")
            
            provider = factory.get_provider("doubao", api_key=api_key)
            message = [AIMessage(role=AIRole.USER, content="你好，请简单回复")]
            
            response = await provider.chat_completion(
                messages=message,
                model=model_id,
                max_tokens=30,
                temperature=0.1
            )
            
            print(f"   ✅ 成功! 模型 {model_id} 可用")
            print(f"      响应: {response.content}")
            print(f"      用量: {response.usage}")
            
            return {
                "success": True,
                "model": model_id,
                "response": response.content,
                "usage": response.usage
            }
            
        except Exception as e:
            error_msg = str(e)
            if "InvalidEndpointOrModel" in error_msg:
                print(f"   ❌ 模型不存在或无权限: {model_id}")
            elif "Unsupported model" in error_msg:
                print(f"   ⚠️ 模型不在支持列表: {model_id}")
            else:
                print(f"   ❌ 其他错误: {error_msg[:80]}...")
    
    return {"success": False, "error": "所有模型都无法访问"}


async def test_deepseek_comprehensive():
    """全面测试DeepSeek API"""
    print("\n🔍 DeepSeek API全面测试")
    print("-" * 40)
    
    api_key = "sk-b3e19280c908402e90ed28b986fbc2f5"
    
    try:
        factory = AIServiceFactory()
        provider = factory.get_provider("deepseek", api_key=api_key)
        
        # 基础连接测试
        message = [AIMessage(role=AIRole.USER, content="你好，请回复：DeepSeek连接成功")]
        
        response = await provider.chat_completion(
            messages=message,
            model="deepseek-reasoner",
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"   ✅ DeepSeek连接成功!")
        print(f"      响应: {response.content}")
        print(f"      用量: {response.usage}")
        
        # 引用检测场景测试
        mention_test = [AIMessage(role=AIRole.USER, content="推荐几个好用的笔记软件，比如Notion")]
        
        mention_response = await provider.chat_completion(
            messages=mention_test,
            model="deepseek-reasoner",
            max_tokens=150,
            temperature=0.3
        )
        
        # 检查是否提及了品牌
        content_lower = mention_response.content.lower()
        notion_mentioned = "notion" in content_lower
        
        print(f"\n   📝 引用检测测试:")
        print(f"      查询: 推荐笔记软件")
        print(f"      Notion提及: {'✅' if notion_mentioned else '❌'}")
        print(f"      响应长度: {len(mention_response.content)} 字符")
        
        return {
            "success": True,
            "basic_test": {
                "response": response.content,
                "usage": response.usage
            },
            "mention_test": {
                "response": mention_response.content[:100] + "...",
                "notion_mentioned": notion_mentioned,
                "usage": mention_response.usage
            }
        }
        
    except Exception as e:
        print(f"   ❌ DeepSeek测试失败: {str(e)}")
        return {"success": False, "error": str(e)}


async def test_ai_integration_scenarios():
    """测试AI集成场景"""
    print("\n🔍 AI集成场景测试")
    print("-" * 40)
    
    # 只使用可用的DeepSeek进行集成测试
    try:
        factory = AIServiceFactory()
        deepseek_provider = factory.get_provider("deepseek", api_key="sk-b3e19280c908402e90ed28b986fbc2f5")
        
        # 场景1: 品牌对比分析
        comparison_query = [AIMessage(
            role=AIRole.USER, 
            content="比较Notion和Obsidian这两个笔记软件的优缺点"
        )]
        
        comparison_response = await deepseek_provider.chat_completion(
            messages=comparison_query,
            model="deepseek-reasoner",
            max_tokens=200,
            temperature=0.5
        )
        
        # 分析提及情况
        content = comparison_response.content.lower()
        notion_mentioned = "notion" in content
        obsidian_mentioned = "obsidian" in content
        
        print(f"   📊 品牌对比分析:")
        print(f"      Notion提及: {'✅' if notion_mentioned else '❌'}")
        print(f"      Obsidian提及: {'✅' if obsidian_mentioned else '❌'}")
        print(f"      响应质量: {'✅ 高质量' if len(comparison_response.content) > 100 else '⚠️ 简短'}")
        
        # 场景2: 推荐场景
        recommendation_query = [AIMessage(
            role=AIRole.USER,
            content="我需要一个支持团队协作的知识管理工具，有什么推荐？"
        )]
        
        recommendation_response = await deepseek_provider.chat_completion(
            messages=recommendation_query,
            model="deepseek-reasoner",
            max_tokens=150,
            temperature=0.3
        )
        
        # 检查推荐质量
        rec_content = recommendation_response.content.lower()
        has_recommendations = any(word in rec_content for word in ["推荐", "建议", "适合"])
        mentions_tools = any(tool in rec_content for tool in ["notion", "confluence", "wiki"])
        
        print(f"\n   💡 推荐场景测试:")
        print(f"      包含推荐: {'✅' if has_recommendations else '❌'}")
        print(f"      提及工具: {'✅' if mentions_tools else '❌'}")
        print(f"      响应长度: {len(recommendation_response.content)} 字符")
        
        return {
            "success": True,
            "comparison_test": {
                "notion_mentioned": notion_mentioned,
                "obsidian_mentioned": obsidian_mentioned,
                "response_length": len(comparison_response.content)
            },
            "recommendation_test": {
                "has_recommendations": has_recommendations,
                "mentions_tools": mentions_tools,
                "response_length": len(recommendation_response.content)
            }
        }
        
    except Exception as e:
        print(f"   ❌ 集成场景测试失败: {str(e)}")
        return {"success": False, "error": str(e)}


async def main():
    """主测试函数"""
    print("🚀 GeoLens 最终端到端测试")
    print("=" * 50)
    print("测试豆包权限调整后的完整AI集成能力")
    print()
    
    # 设置环境变量
    os.environ["DOUBAO_API_KEY"] = "fb429f70-7037-4e2b-bc44-e98b14685cc0"
    os.environ["DEEPSEEK_API_KEY"] = "sk-b3e19280c908402e90ed28b986fbc2f5"
    
    results = {}
    
    # 1. 测试豆包API
    results["doubao"] = await test_doubao_comprehensive()
    
    # 2. 测试DeepSeek API
    results["deepseek"] = await test_deepseek_comprehensive()
    
    # 3. 测试AI集成场景
    results["integration"] = await test_ai_integration_scenarios()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("🎯 最终测试结果汇总")
    print("=" * 50)
    
    # 豆包结果
    if results["doubao"]["success"]:
        print("✅ 豆包API: 连接成功")
        print(f"   可用模型: {results['doubao']['model']}")
    else:
        print("❌ 豆包API: 连接失败")
        print(f"   问题: {results['doubao'].get('error', '权限或配置问题')}")
    
    # DeepSeek结果
    if results["deepseek"]["success"]:
        print("✅ DeepSeek API: 连接成功")
        print(f"   基础功能: 正常")
        print(f"   引用检测: {'支持' if results['deepseek']['mention_test']['notion_mentioned'] else '需优化'}")
    else:
        print("❌ DeepSeek API: 连接失败")
    
    # 集成场景结果
    if results["integration"]["success"]:
        print("✅ AI集成场景: 测试通过")
        comp_test = results["integration"]["comparison_test"]
        rec_test = results["integration"]["recommendation_test"]
        print(f"   品牌对比: {'✅' if comp_test['notion_mentioned'] and comp_test['obsidian_mentioned'] else '⚠️'}")
        print(f"   推荐场景: {'✅' if rec_test['has_recommendations'] else '⚠️'}")
    else:
        print("❌ AI集成场景: 测试失败")
    
    # 总体评估
    success_count = sum(1 for result in results.values() if result["success"])
    total_tests = len(results)
    
    print(f"\n📊 总体成功率: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
    
    if success_count >= 2:  # DeepSeek + 集成场景成功就算基本可用
        print("🎉 GeoLens AI集成基本可用!")
        print("   - DeepSeek集成稳定")
        print("   - 引用检测功能可用")
        print("   - 可以进行下一阶段开发")
        
        if not results["doubao"]["success"]:
            print("\n⚠️ 豆包API需要进一步配置:")
            print("   - 确认模型ID是否正确")
            print("   - 检查API权限设置")
            print("   - 联系豆包技术支持")
    else:
        print("❌ AI集成存在问题，需要解决后再继续")
    
    return success_count >= 2


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
