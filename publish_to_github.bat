@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 GBC MedAI 项目发布到GitHub
echo ================================

REM 检查参数
if "%1"=="" (
    echo ❌ 错误: 请提供您的GitHub用户名
    echo 使用方法: %0 YOUR_GITHUB_USERNAME
    pause
    exit /b 1
)

set GITHUB_USERNAME=%1
set REPO_NAME=gbc-madai

echo 📋 发布信息:
echo    GitHub用户名: %GITHUB_USERNAME%
echo    仓库名称: %REPO_NAME%
echo.

REM 检查是否在正确的目录
if not exist "README.md" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "LICENSE" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 检查git是否安装
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: Git未安装，请先安装Git
    pause
    exit /b 1
)

REM 检查是否已经是git仓库
if exist ".git" (
    echo ⚠️  检测到已存在的Git仓库，将重新初始化
    rmdir /s /q .git
)

echo 📦 步骤1: 初始化Git仓库
git init
if %errorlevel% neq 0 (
    echo ❌ Git初始化失败
    pause
    exit /b 1
)
echo ✅ Git仓库初始化完成

echo 📝 步骤2: 配置Git用户信息
git config --global user.name >nul 2>&1
if %errorlevel% neq 0 (
    set /p git_username="请输入您的Git用户名: "
    git config --global user.name "!git_username!"
)

git config --global user.email >nul 2>&1
if %errorlevel% neq 0 (
    set /p git_email="请输入您的Git邮箱: "
    git config --global user.email "!git_email!"
)

echo 📁 步骤3: 添加所有文件到Git
git add .
if %errorlevel% neq 0 (
    echo ❌ 文件添加失败
    pause
    exit /b 1
)
echo ✅ 文件添加完成

echo 💾 步骤4: 创建初始提交
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

if %errorlevel% neq 0 (
    echo ❌ 提交创建失败
    pause
    exit /b 1
)
echo ✅ 初始提交创建完成

echo 🌿 步骤5: 设置主分支
git branch -M main
if %errorlevel% neq 0 (
    echo ❌ 分支设置失败
    pause
    exit /b 1
)
echo ✅ 主分支设置完成

echo 🔗 步骤6: 添加远程仓库
set REMOTE_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
git remote add origin %REMOTE_URL%
if %errorlevel% neq 0 (
    echo ❌ 远程仓库添加失败
    pause
    exit /b 1
)
echo ✅ 远程仓库添加完成: %REMOTE_URL%

echo 🚀 步骤7: 推送到GitHub
echo ⚠️  即将推送到GitHub，请确保您已经在GitHub上创建了仓库: %REPO_NAME%
pause

git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ 推送失败，可能需要身份验证
    echo.
    echo 💡 解决方案:
    echo 1. 使用GitHub Personal Access Token
    echo 2. 配置SSH密钥
    echo 3. 检查仓库是否已创建
    pause
    exit /b 1
)
echo ✅ 代码推送成功！

echo 🏷️  步骤8: 创建版本标签
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
if %errorlevel% neq 0 (
    echo ❌ 标签推送失败
    pause
    exit /b 1
)
echo ✅ 版本标签创建并推送完成

echo.
echo 🎉 项目发布成功！
echo ================================
echo.
echo 📋 发布信息:
echo    仓库地址: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo    版本标签: v1.0.0
echo    项目大小: 234MB (已优化)
echo.
echo 🔗 下一步操作:
echo 1. 访问GitHub仓库页面设置项目信息
echo 2. 添加Topics标签提高可发现性
echo 3. 上传大文件到网盘并更新下载链接
echo 4. 在GitHub上创建Release发布
echo.
echo 📊 推荐的Topics标签:
echo    ai, medical-assistant, fastapi, vue3, chatbot, deepseek,
echo    ollama, search-engine, typescript, python, healthcare,
echo    machine-learning, conversational-ai, web-application, open-source
echo.
echo 🌟 感谢您选择开源！
echo.
pause
