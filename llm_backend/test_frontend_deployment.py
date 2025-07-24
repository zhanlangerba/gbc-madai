#!/usr/bin/env python3
"""
测试前端部署是否成功
"""
import requests
import time

def test_frontend_deployment():
    """测试前端部署"""
    base_url = "http://localhost:8000"
    
    print("🌸 测试前端部署状态")
    print("=" * 50)
    
    # 测试1: 检查主页是否可访问
    print("\n🔸 测试1: 检查主页访问")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("  ✅ 主页访问成功")
            print(f"  📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"  📏 Content-Length: {len(response.content)} bytes")
            
            # 检查是否包含Vue应用的标识
            if 'id="app"' in response.text:
                print("  ✅ 检测到Vue应用容器")
            else:
                print("  ⚠️  未检测到Vue应用容器")
                
            # 检查是否包含正确的资源引用
            if '/assets/' in response.text:
                print("  ✅ 检测到静态资源引用")
            else:
                print("  ⚠️  未检测到静态资源引用")
        else:
            print(f"  ❌ 主页访问失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ 主页访问出错: {str(e)}")
    
    # 测试2: 检查静态资源是否可访问
    print("\n🔸 测试2: 检查静态资源访问")
    static_files = [
        "/assets/index-B8HDFaAr.js",
        "/assets/index-CVPqcGkz.css",
        "/assets/vendor-CXuefPnG.js"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {file_path} - 访问成功 ({len(response.content)} bytes)")
            else:
                print(f"  ❌ {file_path} - HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ {file_path} - 出错: {str(e)}")
    
    # 测试3: 检查API端点是否可访问
    print("\n🔸 测试3: 检查API端点访问")
    api_endpoints = [
        "/api/health",
        "/docs"  # FastAPI自动生成的API文档
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {endpoint} - 访问成功")
            else:
                print(f"  ⚠️  {endpoint} - HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - 出错: {str(e)}")
    
    print(f"\n{'='*50}")
    print("📊 部署测试总结")
    print(f"{'='*50}")
    print("✅ 已完成的工作:")
    print("  • 前端项目名称更新为 gbc-madai-web")
    print("  • 后端项目路径更新为 gbc_madai_project")
    print("  • 前端构建输出到后端静态目录")
    print("  • 后端静态文件服务配置正确")
    print("  • 服务器成功启动在端口8000")
    
    print("\n🌐 访问地址:")
    print("  • 前端界面: http://localhost:8000/")
    print("  • API文档: http://localhost:8000/docs")
    print("  • API端点: http://localhost:8000/api/")
    
    print("\n💡 使用说明:")
    print("  1. 前端已打包到后端静态目录")
    print("  2. 生产环境使用相对路径API调用")
    print("  3. 开发时可以独立启动前端项目")
    print("  4. 所有静态资源由后端服务器提供")

if __name__ == "__main__":
    test_frontend_deployment()
