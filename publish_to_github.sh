#!/bin/bash

# GBC MedAI 项目发布到GitHub的自动化脚本
# 使用方法: ./publish_to_github.sh YOUR_GITHUB_USERNAME

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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

# 检查参数
if [ $# -eq 0 ]; then
    print_error "请提供您的GitHub用户名"
    echo "使用方法: $0 YOUR_GITHUB_USERNAME"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="gbc-madai"

print_message "🚀 开始发布 GBC MedAI 项目到GitHub"
print_message "GitHub用户名: $GITHUB_USERNAME"
print_message "仓库名称: $REPO_NAME"

# 检查是否在正确的目录
if [ ! -f "README.md" ] || [ ! -f "LICENSE" ]; then
    print_error "请在项目根目录运行此脚本"
    exit 1
fi

# 检查git是否安装
if ! command -v git &> /dev/null; then
    print_error "Git未安装，请先安装Git"
    exit 1
fi

# 检查是否已经是git仓库
if [ -d ".git" ]; then
    print_warning "检测到已存在的Git仓库，将重新初始化"
    rm -rf .git
fi

print_step "1. 初始化Git仓库"
git init
print_message "✅ Git仓库初始化完成"

print_step "2. 配置Git用户信息（如果需要）"
if [ -z "$(git config --global user.name)" ]; then
    read -p "请输入您的Git用户名: " git_username
    git config --global user.name "$git_username"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "请输入您的Git邮箱: " git_email
    git config --global user.email "$git_email"
fi

print_step "3. 添加所有文件到Git"
git add .
print_message "✅ 文件添加完成"

print_step "4. 创建初始提交"
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

Ready for production deployment and community contributions! 🚀"

print_message "✅ 初始提交创建完成"

print_step "5. 设置主分支"
git branch -M main
print_message "✅ 主分支设置完成"

print_step "6. 添加远程仓库"
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
git remote add origin "$REMOTE_URL"
print_message "✅ 远程仓库添加完成: $REMOTE_URL"

print_step "7. 推送到GitHub"
print_warning "即将推送到GitHub，请确保您已经在GitHub上创建了仓库: $REPO_NAME"
read -p "按Enter继续，或Ctrl+C取消..."

# 推送代码
if git push -u origin main; then
    print_message "✅ 代码推送成功！"
else
    print_error "推送失败，可能需要身份验证"
    print_message "请尝试以下解决方案："
    echo "1. 使用GitHub Personal Access Token"
    echo "2. 配置SSH密钥"
    echo "3. 检查仓库是否已创建"
    exit 1
fi

print_step "8. 创建版本标签"
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

git push origin v1.0.0
print_message "✅ 版本标签创建并推送完成"

print_step "9. 发布完成总结"
echo ""
print_message "🎉 项目发布成功！"
echo ""
echo "📋 发布信息："
echo "   仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "   版本标签: v1.0.0"
echo "   项目大小: 234MB (已优化)"
echo ""
echo "🔗 下一步操作："
echo "1. 访问GitHub仓库页面设置项目信息"
echo "2. 添加Topics标签提高可发现性"
echo "3. 上传大文件到网盘并更新下载链接"
echo "4. 在GitHub上创建Release发布"
echo ""
echo "📊 推荐的Topics标签："
echo "   ai, medical-assistant, fastapi, vue3, chatbot, deepseek,"
echo "   ollama, search-engine, typescript, python, healthcare,"
echo "   machine-learning, conversational-ai, web-application, open-source"
echo ""
print_message "感谢您选择开源！🌟"
