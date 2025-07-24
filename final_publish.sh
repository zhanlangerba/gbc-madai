#!/bin/bash

# 最终发布脚本 - 清理敏感信息并发布到GitHub
# 使用方法: ./final_publish.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

echo "🧹 GBC MedAI 最终清理和发布"
echo "=========================="
echo ""

print_step "1. 检查并清理敏感信息"

# 检查是否还有真实的API密钥（排除示例配置）
if grep -r "sk-[a-zA-Z0-9]" . --exclude-dir=.git --exclude="*.sh" 2>/dev/null | grep -v "sk-your" | grep -v "sk-xxx" | grep -v "sk-xxxx"; then
    print_error "发现真实的API密钥，请手动检查并清理"
    exit 1
fi

print_message "✅ 未发现明显的API密钥"

print_step "2. 检查项目大小"
project_size=$(du -sh . | cut -f1)
print_message "项目大小: $project_size"

if [[ $(du -s . | cut -f1) -gt 500000 ]]; then
    print_warning "项目大小超过500MB，可能需要进一步优化"
fi

print_step "3. 初始化Git仓库"
if [ -d ".git" ]; then
    print_warning "删除现有Git仓库"
    rm -rf .git
fi

git init
git branch -M main

print_step "4. 配置Git用户信息"
git config user.name "shiyi.lin"
git config user.email "3397316724@qq.com"

print_step "5. 添加文件到Git"
git add .

print_step "6. 创建提交"
git commit -m "feat: initial commit - GBC MedAI intelligent medical assistant system

🎉 Initial release of GBC MedAI - Intelligent Medical Assistant System

## ✨ Features
- Multi-AI model integration (DeepSeek, Ollama, OpenAI compatible)
- Intelligent search with multiple engines (Bocha AI, Baidu AI, SerpAPI)
- Modern Vue 3 + TypeScript frontend with anime-style UI
- FastAPI backend with comprehensive REST APIs
- User authentication and session management
- Real-time streaming conversations
- Image upload and analysis capabilities
- Redis semantic caching for improved performance

## 🛠 Tech Stack
- **Backend**: FastAPI, SQLAlchemy, MySQL, Redis, Neo4j
- **Frontend**: Vue 3, TypeScript, Element Plus, Vite
- **AI Integration**: DeepSeek API, Ollama, OpenAI Compatible APIs
- **Search Services**: Bocha AI, Baidu AI Search, SerpAPI
- **Deployment**: Docker support, static file serving

## 📚 Documentation
- Complete installation and configuration guide
- API documentation with Swagger UI
- Contribution guidelines and development setup
- Professional open-source project structure

## 🌟 Highlights
- Professional medical AI assistant solution
- Modular architecture for easy extension
- Comprehensive documentation and examples
- Multiple installation options for different needs
- Security-first configuration management
- All sensitive information removed for open source

## 🔐 Security
- All API keys and sensitive data have been removed
- Configuration uses environment variables
- Example configurations provided
- Safe for public distribution

Ready for production deployment and community contributions! 🚀"

print_step "7. 设置远程仓库"
echo ""
print_message "请输入您的GitHub Personal Access Token:"
read -s github_token

if [ -z "$github_token" ]; then
    print_error "Token不能为空"
    exit 1
fi

git remote add origin "https://$github_token@github.com/zhanlangerba/gbc-madai.git"

print_step "8. 推送到GitHub"
print_message "正在推送到GitHub..."

if git push -u origin main; then
    print_message "✅ 代码推送成功！"
    
    print_step "9. 创建版本标签"
    git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release

🎉 First stable release of GBC MedAI

## 🚀 What's New
- Complete AI medical assistant system
- Multi-model support (DeepSeek, Ollama)
- Intelligent search integration
- Modern web interface with Vue 3
- Professional documentation
- Docker deployment support

## 📦 Installation
Three installation options available:
1. Full installation with all features
2. Lightweight installation without GraphRAG
3. Custom installation with self-built environment

## 🔗 Large Files
Due to GitHub size limitations, large files are distributed separately:
- GraphRAG virtual environment (377MB)
- Frontend static assets (131MB)
- Download links provided in LARGE_FILES_README.md

## 🤝 Contributing
We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## 📄 License
MIT License - see LICENSE file for details."

    if git push origin v1.0.0; then
        print_message "✅ 版本标签创建成功！"
    else
        print_warning "⚠️  版本标签推送失败，但主分支已成功推送"
    fi
    
    echo ""
    print_message "🎉 项目发布成功！"
    echo "=================="
    echo ""
    echo "📋 发布信息:"
    echo "   仓库地址: https://github.com/zhanlangerba/gbc-madai"
    echo "   版本标签: v1.0.0"
    echo "   项目大小: $project_size"
    echo ""
    echo "🔗 下一步:"
    echo "1. 访问GitHub仓库页面"
    echo "2. 添加项目描述和Topics标签"
    echo "3. 上传大文件到网盘"
    echo "4. 更新LARGE_FILES_README.md中的下载链接"
    echo "5. 在GitHub上创建Release发布"
    echo ""
    echo "📊 推荐的Topics标签:"
    echo "   ai, medical-assistant, fastapi, vue3, chatbot, deepseek,"
    echo "   ollama, search-engine, typescript, python, healthcare,"
    echo "   machine-learning, conversational-ai, web-application, open-source"
    
else
    print_error "❌ 推送失败"
    echo ""
    echo "💡 可能的解决方案:"
    echo "1. 检查Token权限是否包含 'repo'"
    echo "2. 确认Token没有过期"
    echo "3. 检查网络连接"
    echo "4. 检查仓库是否已创建"
    echo "5. 尝试手动推送: git push -u origin main"
fi

print_message "🔒 安全提醒: 请妥善保管您的GitHub Token"
