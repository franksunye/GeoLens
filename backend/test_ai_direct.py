#!/usr/bin/env python3
"""
直接测试AI连接的脚本
"""

import asyncio
import os
import sys
sys.path.append('/mnt/persist/workspace/backend')

from app.services.ai import AIServiceFactory, AIMessage, AIRole


async def test_doubao_connection():
    """测试豆包连接"""
    print("🔍 测试豆包API连接...")
    
    try:
        # 设置API密钥
        os.environ["DOUBAO_API_KEY"] = "fb429f70-7037-4e2b-bc44-e98b14685cc0"
        
        # 创建AI服务工厂
        factory = AIServiceFactory()
        doubao_provider = factory.get_provider("doubao", api_key="fb429f70-7037-4e2b-bc44-e98b14685cc0")
        
        # 测试消息
        test_message = [
            AIMessage(role=AIRole.USER, content="你好，请回复'豆包连接成功'")
        ]
        
        # 调用API
        response = await doubao_provider.chat_completion(
            messages=test_message,
            model="doubao-lite-32k",
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"✅ 豆包连接成功!")
        print(f"   响应: {response.content}")
        print(f"   提供商: {response.provider}")
        print(f"   模型: {response.model}")
        print(f"   用量: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ 豆包连接失败: {str(e)}")
        return False


async def test_deepseek_connection():
    """测试DeepSeek连接"""
    print("\n🔍 测试DeepSeek API连接...")
    
    try:
        # 设置API密钥
        os.environ["DEEPSEEK_API_KEY"] = "sk-b3e19280c908402e90ed28b986fbc2f5"
        
        # 创建AI服务工厂
        factory = AIServiceFactory()
        deepseek_provider = factory.get_provider("deepseek", api_key="sk-b3e19280c908402e90ed28b986fbc2f5")
        
        # 测试消息
        test_message = [
            AIMessage(role=AIRole.USER, content="Hello, please reply 'DeepSeek connection successful'")
        ]
        
        # 调用API
        response = await deepseek_provider.chat_completion(
            messages=test_message,
            model="deepseek-reasoner",
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"✅ DeepSeek连接成功!")
        print(f"   响应: {response.content}")
        print(f"   提供商: {response.provider}")
        print(f"   模型: {response.model}")
        print(f"   用量: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek连接失败: {str(e)}")
        return False


async def test_basic_ai_functionality():
    """测试基础AI功能"""
    print("\n🔍 测试基础AI功能...")

    try:
        # 设置API密钥
        os.environ["DOUBAO_API_KEY"] = "fb429f70-7037-4e2b-bc44-e98b14685cc0"

        # 创建AI服务工厂
        factory = AIServiceFactory()
        doubao_provider = factory.get_provider("doubao", api_key="fb429f70-7037-4e2b-bc44-e98b14685cc0")

        # 测试引用检测相关的AI调用
        test_message = [
            AIMessage(role=AIRole.USER, content="推荐几个好用的笔记软件，请提及Notion和Obsidian")
        ]

        response = await doubao_provider.chat_completion(
            messages=test_message,
            model="doubao-lite-32k",
            max_tokens=200,
            temperature=0.3
        )

        print(f"✅ 基础AI功能测试成功!")
        print(f"   响应长度: {len(response.content)} 字符")
        print(f"   响应内容: {response.content[:150]}...")

        # 简单检查是否提及了品牌
        content_lower = response.content.lower()
        notion_mentioned = "notion" in content_lower
        obsidian_mentioned = "obsidian" in content_lower

        print(f"\n   品牌提及检查:")
        print(f"     Notion: {'✅' if notion_mentioned else '❌'}")
        print(f"     Obsidian: {'✅' if obsidian_mentioned else '❌'}")

        return True

    except Exception as e:
        print(f"❌ 基础AI功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🚀 GeoLens 端到端测试开始")
    print("=" * 50)
    
    results = []
    
    # 测试豆包连接
    results.append(await test_doubao_connection())
    
    # 测试DeepSeek连接
    results.append(await test_deepseek_connection())
    
    # 测试基础AI功能
    results.append(await test_basic_ai_functionality())
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("🎯 测试结果汇总:")
    
    test_names = ["豆包连接", "DeepSeek连接", "基础AI功能"]
    success_count = 0
    
    for i, (name, success) in enumerate(zip(test_names, results)):
        status = "✅" if success else "❌"
        print(f"   {status} {name}")
        if success:
            success_count += 1
    
    print(f"\n📊 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("🎉 所有测试通过! GeoLens端到端测试成功!")
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接")
    
    return success_count == len(results)


if __name__ == "__main__":
    asyncio.run(main())
