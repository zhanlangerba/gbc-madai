#!/usr/bin/env python3
"""
测试脚本：验证DeepSeek推理模型配置
确保在不同场景下使用正确的模型
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.deepseek_service import DeepseekService
from app.services.llm_factory import LLMFactory
from app.core.logger import get_logger

logger = get_logger(service="test_reasoning")

async def test_chat_model():
    """测试聊天模型"""
    print("=" * 60)
    print("测试聊天模型 (deepseek-chat)")
    print("=" * 60)
    
    chat_service = DeepseekService(use_reasoning=False)
    print(f"聊天服务使用的模型: {chat_service.model}")
    
    messages = [{"role": "user", "content": "你好，请简单介绍一下自己"}]
    
    try:
        response = await chat_service.generate(messages)
        print(f"聊天响应: {response[:200]}...")
        return True
    except Exception as e:
        print(f"聊天测试失败: {str(e)}")
        return False

async def test_reasoning_model():
    """测试推理模型"""
    print("=" * 60)
    print("测试推理模型 (deepseek-reasoner)")
    print("=" * 60)
    
    reasoning_service = DeepseekService(use_reasoning=True)
    print(f"推理服务使用的模型: {reasoning_service.model}")
    
    messages = [{"role": "user", "content": "请解释量子计算的基本原理，并分析其在密码学中的应用前景"}]
    
    try:
        response = await reasoning_service.generate_reasoning(messages)
        print(f"推理响应: {response[:200]}...")
        return True
    except Exception as e:
        print(f"推理测试失败: {str(e)}")
        return False

async def test_factory_services():
    """测试工厂创建的服务"""
    print("=" * 60)
    print("测试LLM工厂创建的服务")
    print("=" * 60)
    
    # 测试聊天服务
    chat_service = LLMFactory.create_chat_service()
    print(f"工厂创建的聊天服务模型: {getattr(chat_service, 'model', 'N/A')}")
    
    # 测试推理服务
    reasoning_service = LLMFactory.create_reasoner_service()
    print(f"工厂创建的推理服务模型: {getattr(reasoning_service, 'model', 'N/A')}")
    
    return True

def test_environment_variables():
    """测试环境变量配置"""
    print("=" * 60)
    print("测试环境变量配置")
    print("=" * 60)
    
    print(f"DEEPSEEK_MODEL (聊天): {settings.DEEPSEEK_MODEL}")
    print(f"DEEPSEEK_REASON_MODEL (推理): {settings.DEEPSEEK_REASON_MODEL}")
    print(f"CHAT_SERVICE: {settings.CHAT_SERVICE}")
    print(f"REASON_SERVICE: {settings.REASON_SERVICE}")
    print(f"AGENT_SERVICE: {settings.AGENT_SERVICE}")
    
    # 验证配置
    assert settings.DEEPSEEK_MODEL == "deepseek-chat", f"聊天模型应该是deepseek-chat，实际是{settings.DEEPSEEK_MODEL}"
    assert settings.DEEPSEEK_REASON_MODEL == "deepseek-reasoner", f"推理模型应该是deepseek-reasoner，实际是{settings.DEEPSEEK_REASON_MODEL}"
    
    print("✅ 环境变量配置正确")
    return True

async def test_stream_reasoning():
    """测试流式推理"""
    print("=" * 60)
    print("测试流式推理")
    print("=" * 60)
    
    reasoning_service = DeepseekService(use_reasoning=True)
    messages = [{"role": "user", "content": "请分析人工智能的发展趋势"}]
    
    try:
        print("开始流式推理...")
        chunk_count = 0
        async for chunk in reasoning_service.generate_reasoning_stream(messages):
            chunk_count += 1
            if chunk_count <= 3:  # 只显示前3个chunk
                print(f"Chunk {chunk_count}: {chunk[:50]}...")
        
        print(f"✅ 流式推理成功，共收到 {chunk_count} 个数据块")
        return True
    except Exception as e:
        print(f"流式推理测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始DeepSeek推理模型配置测试")
    print(f"当前时间: {asyncio.get_event_loop().time()}")
    
    tests = [
        ("环境变量配置", test_environment_variables),
        ("工厂服务创建", test_factory_services),
        ("聊天模型", test_chat_model),
        ("推理模型", test_reasoning_model),
        ("流式推理", test_stream_reasoning),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 执行测试: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'通过' if result else '失败'}")
        except Exception as e:
            print(f"❌ {test_name}: 异常 - {str(e)}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！推理模型配置正确。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
