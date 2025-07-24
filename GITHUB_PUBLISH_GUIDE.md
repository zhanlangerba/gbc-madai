# GitHub 发布完整指南

## 🎯 发布前准备

### 1. 确认GitHub账号信息
- GitHub用户名: `zhanlangerba`
- 邮箱: `3397316724@qq.com`

### 2. 项目信息
- **仓库名称**: `gbc-madai` (推荐)
- **项目大小**: 234MB (已优化，适合GitHub)
- **大文件**: 508MB (需要网盘分发)

## 🚀 发布步骤

### 方式一：使用自动化脚本（推荐）

#### Linux/Mac 用户：
```bash
cd gbc_madai_project_opensource
chmod +x publish_to_github.sh
./publish_to_github.sh zhanlangerba
```

#### Windows 用户：
```cmd
cd gbc_madai_project_opensource
publish_to_github.bat zhanlangerba
```

### 方式二：手动发布

#### 1. 在GitHub创建仓库
1. 登录 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `gbc-madai`
   - Description: `智能医疗助手系统 - 基于 FastAPI + Vue 3 的 AI 对话和搜索平台`
   - Public (公开)
   - **不要勾选** README、.gitignore、LICENSE

#### 2. 本地Git操作
```bash
# 进入项目目录
cd gbc_madai_project_opensource

# 初始化Git仓库
git init

# 配置用户信息（如果需要）
git config --global user.name "shiyi.lin"
git config --global user.email "3397316724@qq.com"

# 添加所有文件
git add .

# 创建初始提交
git commit -m "feat: initial commit - GBC MedAI intelligent medical assistant system"

# 设置主分支
git branch -M main

# 添加远程仓库
git remote add origin https://github.com/zhanlangerba/gbc-madai.git

# 推送代码
git push -u origin main

# 创建版本标签
git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"
git push origin v1.0.0
```

## 🔐 身份验证

### 选项1：Personal Access Token（推荐）
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. 勾选 `repo` 权限
4. 复制生成的token
5. 推送时使用token作为密码

### 选项2：SSH密钥
```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "3397316724@qq.com"

# 添加到SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

# 复制公钥到GitHub
cat ~/.ssh/id_rsa.pub
# 在GitHub → Settings → SSH and GPG keys 中添加

# 使用SSH URL
git remote set-url origin git@github.com:zhanlangerba/gbc-madai.git
```

## 📊 仓库设置

### 1. 基本信息
- **About**: `智能医疗助手系统 - 基于 FastAPI + Vue 3 的 AI 对话和搜索平台`
- **Website**: 可以填写演示地址（如果有）
- **Topics**: 
  ```
  ai, medical-assistant, fastapi, vue3, chatbot, deepseek, ollama, 
  search-engine, typescript, python, healthcare, machine-learning,
  conversational-ai, web-application, open-source
  ```

### 2. 功能设置
- ✅ Issues
- ✅ Discussions
- ✅ Wiki (可选)
- ✅ Projects (可选)

### 3. 分支保护（可选）
- Settings → Branches → Add rule
- Branch name pattern: `main`
- ✅ Require pull request reviews before merging

## 🎉 创建Release

1. 进入仓库页面
2. 点击 "Releases" → "Create a new release"
3. 选择标签: `v1.0.0`
4. Release title: `v1.0.0 - GBC MedAI 首次公开发布`
5. 描述内容：

```markdown
# 🎉 GBC MedAI v1.0.0 - 首次公开发布

## ✨ 主要功能

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

- **后端**: FastAPI, SQLAlchemy, MySQL, Redis, Neo4j
- **前端**: Vue 3, TypeScript, Element Plus, Vite
- **AI集成**: DeepSeek API, Ollama, OpenAI Compatible APIs
- **搜索服务**: 博查AI, 百度AI搜索, SerpAPI

## 📦 安装方式

提供三种安装选项：
1. **完整安装**: 包含所有功能
2. **轻量安装**: 跳过GraphRAG功能
3. **自建环境**: 使用自动化脚本构建

## 🔗 大文件下载

由于GitHub大小限制，部分大文件需要单独下载：
- GraphRAG虚拟环境 (377MB)
- 前端静态资源 (131MB)

详见 [LARGE_FILES_README.md](LARGE_FILES_README.md)

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
```

## 📋 发布后检查清单

- [ ] 仓库正确显示
- [ ] README.md 正确渲染
- [ ] 所有链接正常工作
- [ ] Topics标签已添加
- [ ] Release已创建
- [ ] 没有敏感信息泄露

## 🔗 大文件处理

### 1. 上传到网盘
将 `gbc_madai_large_files/` 中的文件上传到：
- 百度网盘
- 阿里云盘
- Google Drive
- OneDrive

### 2. 更新下载链接
编辑 `LARGE_FILES_README.md`，更新下载链接部分：

```markdown
## 🔗 下载链接

- **GraphRAG虚拟环境**: [百度网盘链接](your-link-here)
- **静态资源文件**: [百度网盘链接](your-link-here)
- **提取码**: your-code-here
```

## 🆘 常见问题

### 推送失败
- 检查网络连接
- 确认仓库已创建
- 验证身份认证
- 检查分支名称

### 文件过大
- 确认已移除大文件
- 检查 .gitignore 配置
- 使用 `git lfs` (如果需要)

### 权限问题
- 确认GitHub账号权限
- 检查Personal Access Token
- 验证SSH密钥配置

## 📞 获取帮助

如果遇到问题：
1. 查看GitHub官方文档
2. 检查错误信息
3. 搜索相关解决方案
4. 联系技术支持

---

**准备发布您的开源项目！** 🚀
