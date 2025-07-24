# 贡献指南

感谢您对 GBC MedAI 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能

## 🚀 快速开始

### 1. Fork 项目

点击项目页面右上角的 "Fork" 按钮，将项目 fork 到您的 GitHub 账户。

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/gbc-madai.git
cd gbc-madai
```

### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 4. 设置开发环境

```bash
# 安装后端依赖
cd llm_backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 安装前端依赖（如果需要）
cd ../gbc_madai_web
npm install
```

## 📝 开发规范

### 代码风格

#### Python 代码
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 4 个空格缩进
- 行长度不超过 88 字符
- 使用有意义的变量和函数名

#### JavaScript/TypeScript 代码
- 使用 2 个空格缩进
- 使用分号结尾
- 使用 camelCase 命名变量和函数
- 使用 PascalCase 命名组件

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### 类型说明

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 示例

```bash
git commit -m "feat(search): add bocha ai search integration"
git commit -m "fix(auth): resolve token expiration issue"
git commit -m "docs: update installation guide"
```

## 🧪 测试

### 运行测试

```bash
# 后端测试
cd llm_backend
python -m pytest

# 前端测试
cd gbc_madai_web
npm run test
```

### 添加测试

- 为新功能添加单元测试
- 确保测试覆盖率不降低
- 测试文件命名：`test_*.py` 或 `*.test.ts`

## 📋 Pull Request 流程

### 1. 确保代码质量

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档

### 2. 提交 Pull Request

1. 推送您的分支到 GitHub
2. 在 GitHub 上创建 Pull Request
3. 填写 PR 模板中的信息
4. 等待代码审查

### 3. PR 模板

```markdown
## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 变更描述
简要描述您的变更内容

## 测试
- [ ] 添加了新的测试
- [ ] 所有测试通过
- [ ] 手动测试通过

## 相关 Issue
Closes #issue_number
```

## 🐛 报告 Bug

### Bug 报告模板

```markdown
**Bug 描述**
简要描述遇到的问题

**复现步骤**
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

**期望行为**
描述您期望发生的情况

**实际行为**
描述实际发生的情况

**环境信息**
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
- Python 版本: [e.g. 3.9.0]
- 浏览器: [e.g. Chrome 95.0]

**附加信息**
添加任何其他有助于解决问题的信息
```

## 💡 功能建议

### 功能建议模板

```markdown
**功能描述**
简要描述您希望添加的功能

**问题背景**
描述这个功能要解决的问题

**解决方案**
描述您希望的解决方案

**替代方案**
描述您考虑过的其他解决方案

**附加信息**
添加任何其他相关信息或截图
```

## 📚 文档贡献

### 文档类型

- **README.md**: 项目介绍和快速开始
- **API 文档**: API 接口说明
- **用户指南**: 详细使用说明
- **开发文档**: 开发相关说明

### 文档规范

- 使用 Markdown 格式
- 添加适当的标题层级
- 包含代码示例
- 添加必要的图片说明

## 🤝 社区准则

### 行为准则

- 尊重所有参与者
- 使用友善和包容的语言
- 接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 沟通渠道

- **GitHub Issues**: 报告 Bug 和功能建议
- **GitHub Discussions**: 一般讨论和问答
- **Pull Requests**: 代码审查和讨论

## 🏆 贡献者认可

我们会在以下地方认可贡献者：

- README.md 中的贡献者列表
- 发布说明中的感谢
- 项目网站的贡献者页面

## ❓ 需要帮助？

如果您在贡献过程中遇到任何问题，请：

1. 查看现有的 Issues 和 Discussions
2. 创建新的 Issue 或 Discussion
3. 在 PR 中 @mention 维护者

感谢您的贡献！🎉
