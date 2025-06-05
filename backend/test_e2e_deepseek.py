#!/usr/bin/env python3
"""
专门测试DeepSeek的端到端功能
"""

import asyncio
import os
import sys
sys.path.append('/mnt/persist/workspace/backend')

from app.services.ai import AIServiceFactory, AIMessage, AIRole


async def test_deepseek_basic():
    """测试DeepSeek基础功能"""
    print("🔍 测试DeepSeek基础功能...")
    
    try:
        factory = AIServiceFactory()
        provider = factory.get_provider("deepseek", api_key="sk-b3e19280c908402e90ed28b986fbc2f5")
        
        message = [AIMessage(role=AIRole.USER, content="Hello, please reply 'DeepSeek is working'")]
        
        response = await provider.chat_completion(
            messages=message,
            model="deepseek-reasoner",
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"✅ DeepSeek基础功能测试成功!")
        print(f"   响应: {response.content}")
        print(f"   模型: {response.model}")
        print(f"   用量: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek基础功能测试失败: {str(e)}")
        return False


async def test_deepseek_mention_detection():
    """测试DeepSeek引用检测场景"""
    print("\n🔍 测试DeepSeek引用检测场景...")
    
    try:
        factory = AIServiceFactory()
        provider = factory.get_provider("deepseek", api_key="sk-b3e19280c908402e90ed28b986fbc2f5")
        
        # 测试引用检测相关的查询
        test_queries = [
            "推荐几个好用的笔记软件",
            "有哪些团队协作工具？",
            "知识管理系统推荐"
        ]
        
        brands_to_check = ["Notion", "Obsidian", "Roam Research"]
        
        results = []
        
        for i, query in enumerate(test_queries):
            print(f"   测试查询 {i+1}: {query}")
            
            message = [AIMessage(role=AIRole.USER, content=query)]
            
            response = await provider.chat_completion(
                messages=message,
                model="deepseek-reasoner",
                max_tokens=300,
                temperature=0.3
            )
            
            # 简单的品牌提及检测
            content_lower = response.content.lower()
            mentions = {}
            
            for brand in brands_to_check:
                mentioned = brand.lower() in content_lower
                mentions[brand] = mentioned
                status = "✅" if mentioned else "❌"
                print(f"     {status} {brand}")
            
            results.append({
                "query": query,
                "response": response.content,
                "mentions": mentions,
                "response_length": len(response.content),
                "usage": response.usage
            })
        
        # 汇总结果
        total_mentions = sum(
            sum(1 for mentioned in result["mentions"].values() if mentioned)
            for result in results
        )
        
        total_possible = len(test_queries) * len(brands_to_check)
        mention_rate = total_mentions / total_possible if total_possible > 0 else 0
        
        print(f"\n✅ DeepSeek引用检测场景测试完成!")
        print(f"   测试查询数: {len(test_queries)}")
        print(f"   测试品牌数: {len(brands_to_check)}")
        print(f"   总提及数: {total_mentions}/{total_possible}")
        print(f"   提及率: {mention_rate:.2%}")
        
        # 显示一个示例响应
        if results:
            example = results[0]
            print(f"\n   示例响应 (查询: {example['query']}):")
            print(f"   {example['response'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek引用检测场景测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_deepseek_reasoning():
    """测试DeepSeek推理能力"""
    print("\n🔍 测试DeepSeek推理能力...")
    
    try:
        factory = AIServiceFactory()
        provider = factory.get_provider("deepseek", api_key="sk-b3e19280c908402e90ed28b986fbc2f5")
        
        # 测试需要推理的问题
        reasoning_query = """
        请分析以下场景：一个团队需要选择知识管理工具，他们的需求是：
        1. 支持团队协作
        2. 有良好的文档编辑功能
        3. 支持数据库功能
        4. 价格合理
        
        请推荐合适的工具并说明理由。
        """
        
        message = [AIMessage(role=AIRole.USER, content=reasoning_query)]
        
        response = await provider.chat_completion(
            messages=message,
            model="deepseek-reasoner",
            max_tokens=500,
            temperature=0.5
        )
        
        print(f"✅ DeepSeek推理能力测试成功!")
        print(f"   响应长度: {len(response.content)} 字符")
        print(f"   用量: {response.usage}")
        
        # 检查推理质量指标
        content = response.content
        has_analysis = any(word in content.lower() for word in ["分析", "因为", "由于", "考虑", "建议"])
        has_recommendations = any(word in content.lower() for word in ["推荐", "建议", "选择", "适合"])
        has_reasoning = any(word in content.lower() for word in ["理由", "原因", "优势", "特点"])
        
        print(f"\n   推理质量评估:")
        print(f"     包含分析: {'✅' if has_analysis else '❌'}")
        print(f"     包含推荐: {'✅' if has_recommendations else '❌'}")
        print(f"     包含理由: {'✅' if has_reasoning else '❌'}")
        
        print(f"\n   响应内容预览:")
        print(f"   {content[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek推理能力测试失败: {str(e)}")
        return False


async def test_deepseek_concurrent():
    """测试DeepSeek并发调用"""
    print("\n🔍 测试DeepSeek并发调用...")
    
    try:
        factory = AIServiceFactory()
        provider = factory.get_provider("deepseek", api_key="sk-b3e19280c908402e90ed28b986fbc2f5")
        
        # 准备并发任务
        async def single_call(query_id: int):
            message = [AIMessage(role=AIRole.USER, content=f"请简单回答：什么是人工智能？(请求{query_id})")]
            
            response = await provider.chat_completion(
                messages=message,
                model="deepseek-reasoner",
                max_tokens=100,
                temperature=0.1
            )
            
            return {
                "query_id": query_id,
                "success": True,
                "response_length": len(response.content),
                "usage": response.usage
            }
        
        # 执行并发调用
        tasks = [single_call(i) for i in range(1, 4)]  # 3个并发请求
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 分析结果
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        print(f"✅ DeepSeek并发调用测试完成!")
        print(f"   并发请求数: {len(tasks)}")
        print(f"   成功请求数: {len(successful_results)}")
        print(f"   失败请求数: {len(failed_results)}")
        
        if successful_results:
            avg_length = sum(r["response_length"] for r in successful_results) / len(successful_results)
            total_tokens = sum(r["usage"]["total_tokens"] for r in successful_results)
            print(f"   平均响应长度: {avg_length:.1f} 字符")
            print(f"   总消耗Token: {total_tokens}")
        
        return len(successful_results) > 0
        
    except Exception as e:
        print(f"❌ DeepSeek并发调用测试失败: {str(e)}")
        return False


async def main():
    """主函数"""
    print("🚀 GeoLens DeepSeek 端到端测试")
    print("=" * 50)
    
    # 设置环境变量
    os.environ["DEEPSEEK_API_KEY"] = "sk-b3e19280c908402e90ed28b986fbc2f5"
    
    tests = [
        ("DeepSeek基础功能", test_deepseek_basic),
        ("DeepSeek引用检测场景", test_deepseek_mention_detection),
        ("DeepSeek推理能力", test_deepseek_reasoning),
        ("DeepSeek并发调用", test_deepseek_concurrent),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 执行异常: {str(e)}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("🎯 DeepSeek测试结果汇总:")
    
    success_count = 0
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
        if success:
            success_count += 1
    
    print(f"\n📊 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("🎉 所有DeepSeek测试通过! 端到端集成成功!")
    elif success_count > 0:
        print("⚠️ 部分测试通过，DeepSeek基本功能正常")
    else:
        print("❌ 所有测试失败，请检查配置")
    
    return success_count > 0


if __name__ == "__main__":
    asyncio.run(main())
