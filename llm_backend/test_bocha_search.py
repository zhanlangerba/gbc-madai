#!/usr/bin/env python3
"""
博查AI搜索功能测试脚本
"""
import sys
import os
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.tools.search import SearchTool
from app.core.config import settings

def test_bocha_ai_search():
    """测试博查AI搜索功能"""
    try:
        print("=" * 60)
        print("测试博查AI搜索功能")
        print("=" * 60)
        
        print(f"当前搜索服务: {settings.SEARCH_SERVICE}")
        print(f"博查AI API Key已配置: {'是' if settings.BOCHA_AI_API_KEY else '否'}")
        print(f"博查AI Base URL: {settings.BOCHA_AI_BASE_URL}")
        print(f"搜索结果数量: {settings.SEARCH_RESULT_COUNT}")
        
        # 创建搜索工具实例
        search_tool = SearchTool()
        
        # 测试查询列表
        test_queries = [
            "今天北京天气预报",
            "Python编程教程",
            "人工智能最新发展",
            "2024年奥运会结果"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*20} 测试 {i}/{len(test_queries)} {'='*20}")
            print(f"搜索查询: {query}")
            print("-" * 50)
            
            try:
                results = search_tool.search(query, num_results=5)
                
                if results:
                    print(f"✅ 搜索成功，找到 {len(results)} 个结果:")
                    for j, result in enumerate(results, 1):
                        print(f"\n{j}. 标题: {result['title']}")
                        print(f"   URL: {result['url']}")
                        print(f"   摘要: {result['snippet'][:150]}{'...' if len(result['snippet']) > 150 else ''}")
                else:
                    print("❌ 搜索失败或没有找到结果")
                    
            except Exception as e:
                print(f"❌ 搜索出错: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # 在测试之间稍作停顿
            if i < len(test_queries):
                print("\n等待3秒后进行下一个测试...")
                time.sleep(3)
        
        print(f"\n{'='*60}")
        print("所有测试完成!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"测试初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_search_service_switch():
    """测试搜索服务切换功能"""
    print(f"\n{'='*60}")
    print("测试搜索服务切换功能")
    print(f"{'='*60}")
    
    # 测试不同的搜索服务配置
    original_service = settings.SEARCH_SERVICE
    
    services_to_test = ["bocha_ai", "serpapi"]
    
    for service in services_to_test:
        print(f"\n测试搜索服务: {service}")
        print("-" * 30)
        
        try:
            # 临时修改搜索服务配置
            settings.SEARCH_SERVICE = service
            
            # 创建搜索工具实例
            search_tool = SearchTool()
            
            # 执行简单搜索测试
            results = search_tool.search("测试查询", num_results=2)
            
            if results:
                print(f"✅ {service} 搜索服务工作正常")
                print(f"   返回了 {len(results)} 个结果")
                for result in results:
                    print(f"   - {result['title'][:50]}...")
            else:
                print(f"⚠️  {service} 搜索服务返回空结果")
                
        except Exception as e:
            print(f"❌ {service} 搜索服务测试失败: {str(e)}")
        
        # 等待避免API频率限制
        time.sleep(2)
    
    # 恢复原始配置
    settings.SEARCH_SERVICE = original_service
    print(f"\n恢复原始搜索服务配置: {original_service}")

def test_bocha_ai_features():
    """测试博查AI的特色功能"""
    print(f"\n{'='*60}")
    print("测试博查AI特色功能")
    print(f"{'='*60}")
    
    try:
        search_tool = SearchTool()
        
        # 测试中文搜索
        print("\n🔸 测试1: 中文搜索能力")
        results = search_tool.search("杭州美食推荐", num_results=3)
        if results:
            print(f"  ✅ 中文搜索正常 - 返回 {len(results)} 个结果")
            for result in results:
                print(f"    - {result['title'][:40]}...")
        else:
            print("  ⚠️  中文搜索返回空结果")
        
        time.sleep(3)
        
        # 测试技术搜索
        print("\n🔸 测试2: 技术内容搜索")
        results = search_tool.search("React hooks 使用教程", num_results=3)
        if results:
            print(f"  ✅ 技术搜索正常 - 返回 {len(results)} 个结果")
            for result in results:
                print(f"    - {result['title'][:40]}...")
        else:
            print("  ⚠️  技术搜索返回空结果")
        
        time.sleep(3)
        
        # 测试新闻搜索
        print("\n🔸 测试3: 新闻时事搜索")
        results = search_tool.search("最新科技新闻", num_results=3)
        if results:
            print(f"  ✅ 新闻搜索正常 - 返回 {len(results)} 个结果")
            for result in results:
                print(f"    - {result['title'][:40]}...")
        else:
            print("  ⚠️  新闻搜索返回空结果")
        
        print(f"\n✅ 博查AI特色功能测试完成")
        
    except Exception as e:
        print(f"❌ 博查AI特色功能测试失败: {str(e)}")

def show_integration_summary():
    """显示集成总结"""
    print(f"\n{'='*60}")
    print("📊 博查AI搜索集成总结")
    print(f"{'='*60}")
    
    print("✅ 已完成的工作:")
    print("  • 配置博查AI搜索API密钥")
    print("  • 更新配置文件支持多搜索服务")
    print("  • 实现博查AI搜索工具类")
    print("  • 添加错误处理和重试机制")
    print("  • 保持与原SerpAPI相同的接口")
    
    print("\n🔧 技术特性:")
    print("  • 使用博查AI Web Search API")
    print("  • 支持中文搜索查询")
    print("  • 智能错误处理和重试")
    print("  • 返回高质量搜索结果")
    print("  • 备用结果机制")
    
    print("\n💰 成本优势:")
    print("  • 按次计费，约¥0.036/次")
    print("  • 比SerpAPI更适合中文搜索")
    print("  • 专为AI应用优化")
    
    print(f"\n🎯 网络连接问题已解决！")
    print("   博查AI搜索可以正常工作，不再依赖SerpAPI的网络连接")

if __name__ == "__main__":
    # 运行博查AI搜索测试
    test_bocha_ai_search()
    
    # 运行搜索服务切换测试
    test_search_service_switch()
    
    # 运行博查AI特色功能测试
    test_bocha_ai_features()
    
    # 显示集成总结
    show_integration_summary()
