![logo](https://github.com/user-attachments/assets/256af121-3871-41df-9fa0-09e8c612cd78)


<div align="center">

![GBC MedAI Logo](https://img.shields.io/badge/GBC-MedAI-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Vue](https://img.shields.io/badge/Vue-3.0+-green?style=for-the-badge&logo=vue.js)

一个基于 FastAPI + Vue 3 的智能医疗助手系统，集成多种 AI 模型和智能搜索功能。

[🚀 快速开始](#快速开始) • [📖 文档](#api-文档) • [🤝 贡献](#贡献指南) • [📄 许可证](#许可证)

</div>

## ✨ 功能特性

### 🤖 AI 能力
- **多模型支持**: DeepSeek、Ollama 本地模型、OpenAI 兼容接口
- **智能对话**: 支持流式响应和上下文记忆
- **推理能力**: 集成 DeepSeek Reasoner 进行复杂推理
- **视觉理解**: 支持图片上传和分析

### 🔍 智能搜索
- **多搜索引擎**: 博查AI、百度AI搜索、SerpAPI
- **实时信息**: 获取最新医疗资讯和研究进展
- **智能路由**: 自动选择最适合的搜索策略

### 💬 对话系统
- **会话管理**: 多会话支持，历史记录保存
- **用户系统**: 注册、登录、个人设置
- **实时通信**: WebSocket 支持流式对话

### 🎨 现代化界面
- **二次元风格**: 精美的动漫风格UI设计
- **响应式布局**: 支持桌面和移动端
- **交互动画**: 丰富的动画效果和反馈

## 🛠 技术栈

### 后端技术
- **框架**: FastAPI (高性能异步Web框架)
- **数据库**: MySQL + Redis + Neo4j
- **AI集成**: DeepSeek API, Ollama, OpenAI Compatible APIs
- **搜索服务**: 博查AI, 百度AI搜索, SerpAPI
- **缓存**: Redis 语义缓存
- **日志**: 结构化日志系统

### 前端技术
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **状态管理**: Pinia
- **构建工具**: Vite
- **样式**: CSS3 + 动画效果

### AI技术
- **AI框架**: LangGraph+GraphRag 

- 
## 🚀 快速开始

### 📋 环境要求

- **Python**: 3.8 或更高版本
- **Node.js**: 16 或更高版本 (仅开发模式需要)
- **数据库**: MySQL 8.0+, Redis 6.0+
- **可选**: Neo4j 4.0+ (用于知识图谱)

### 📦 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/gbc-madai.git
cd gbc-madai
```

2. **后端设置**
```bash
cd llm_backend
pip install -r requirements.txt
```

3. **环境配置**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件，填入您的API密钥和数据库信息
nano .env
```

4. **数据库初始化**
```bash
# 创建MySQL数据库
mysql -u root -p -e "CREATE DATABASE assist_gen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

5. **启动服务**
```bash
# 启动后端服务
python run.py

# 服务将在 http://localhost:8000 启动
# 前端界面: http://localhost:8000/
# API文档: http://localhost:8000/docs
```

### 🔧 开发模式

如果需要前端开发模式：

```bash
# 在新终端中启动前端开发服务器
cd ../gbc_madai_web
npm install
npm run dev

# 前端开发服务器: http://localhost:3000
```

## 📖 配置说明

### 🤖 AI 模型配置

```env
# DeepSeek 配置
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_REASON_MODEL=deepseek-reasoner

# 本地 Ollama 配置（可选）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:32b
```

### 🔍 搜索服务配置

```env
# 选择搜索服务
SEARCH_SERVICE=bocha_ai  # bocha_ai, baidu_ai, serpapi

# 博查AI（推荐）
BOCHA_AI_API_KEY=sk-your-bocha-key

# 百度AI搜索
BAIDU_AI_SEARCH_API_KEY=your-baidu-key

# SerpAPI
SERPAPI_KEY=your-serpapi-key
```

### 🗄️ 数据库配置

```env
# MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=assist_gen

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Neo4j（可选）
NEO4J_URL=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

## 📚 API 文档

启动服务后，您可以访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要 API 端点

- `POST /api/chat` - 智能对话
- `POST /api/search` - 智能搜索
- `POST /api/token` - 用户认证
- `GET /api/conversations/user/{user_id}` - 获取用户会话
- `POST /api/upload/image` - 图片上传

## 🏗️ 项目结构

```
gbc-madai/
├── llm_backend/                 # 后端代码
│   ├── app/                    # 应用核心
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   ├── tools/             # 工具模块
│   │   └── utils/             # 工具函数
│   ├── static/                # 前端构建文件
│   ├── main.py                # FastAPI 应用入口
│   ├── run.py                 # 启动脚本
│   └── requirements.txt       # Python 依赖
├── gbc_madai_web/             # 前端源码（开发用）
│   ├── src/                   # Vue 源码
│   ├── package.json           # 前端依赖
│   └── vite.config.ts         # 构建配置
└── README.md                  # 项目文档
```
## ⭐️ 前置条件

- 前端链接: https://pan.baidu.com/s/1KTROmn78XhhcuYBOfk0iUQ?pwd=wi8k 提取码: wi8k
- GraphRag链接：链接: https://pan.baidu.com/s/1dg6YxN_a4wZCXrmHBPGj_Q?pwd=hppu 提取码: hppu


## 🚀 部署

### Docker 部署（推荐）

```bash
# 构建镜像
docker build -t gbc-madai .

# 运行容器
docker run -d -p 8000:8000 --env-file .env gbc-madai
```

### 传统部署

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

1. **Fork** 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 **Pull Request**

### 开发规范

- 遵循 PEP 8 Python 代码规范
- 为新功能添加测试
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
## 🛠 更新计划

- 7月更新客服深度搜索以及前端代码
- 8月更新客服联网搜索


## 🙏 致谢

感谢以下开源项目和服务：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库
- [DeepSeek](https://www.deepseek.com/) - 强大的 AI 模型服务
- [博查AI](https://open.bochaai.com/) - 专业的搜索服务

## 📞 联系方式

- **项目链接**: [https://github.com/yourusername/gbc-madai](https://github.com/yourusername/gbc-madai)
- **问题反馈**: [Issues](https://github.com/yourusername/gbc-madai/issues)
- **功能建议**: [Discussions](https://github.com/yourusername/gbc-madai/discussions)

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️**

Made with ❤️ by GBC MedAI Team

</div>
