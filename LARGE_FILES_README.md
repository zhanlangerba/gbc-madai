# 大文件下载说明

由于GitHub对文件大小有限制，我们将一些大文件单独打包提供下载。

## 📦 大文件包含内容

### 1. GraphRAG 虚拟环境 (`graphrag_venv.tar.gz`)
- **大小**: ~1.5GB
- **内容**: GraphRAG功能所需的Python虚拟环境
- **路径**: 应解压到 `llm_backend/app/graphrag/venv/`

### 2. 静态资源文件 (`static_assets.tar.gz`)
- **大小**: ~132MB  
- **内容**: 前端背景动画文件
- **路径**: 应解压到 `llm_backend/static/assets/`

## 🔗 下载链接

> **注意**: 以下链接将在项目发布后提供

- **GraphRAG虚拟环境**: [下载链接待更新]
- **静态资源文件**: [下载链接待更新]

## 📥 安装步骤

### 方式一：完整安装（推荐新用户）

1. **克隆项目**
```bash
git clone https://github.com/yourusername/gbc-madai.git
cd gbc-madai
```

2. **下载大文件包**
```bash
# 下载 graphrag_venv.tar.gz 和 static_assets.tar.gz
# 放置到项目根目录
```

3. **解压大文件**
```bash
# 解压GraphRAG虚拟环境
tar -xzf graphrag_venv.tar.gz -C llm_backend/app/graphrag/

# 解压静态资源
tar -xzf static_assets.tar.gz -C llm_backend/static/
```

4. **继续常规安装**
```bash
cd llm_backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件配置
python run.py
```

### 方式二：轻量安装（不使用GraphRAG）

如果您不需要GraphRAG功能，可以跳过GraphRAG虚拟环境的下载：

1. **克隆项目**
```bash
git clone https://github.com/yourusername/gbc-madai.git
cd gbc-madai
```

2. **仅下载静态资源**
```bash
# 下载 static_assets.tar.gz
tar -xzf static_assets.tar.gz -C llm_backend/static/
```

3. **禁用GraphRAG功能**
在 `.env` 文件中设置：
```env
# 禁用GraphRAG功能
ENABLE_GRAPHRAG=false
```

4. **安装依赖**
```bash
cd llm_backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件
python run.py
```

### 方式三：自建GraphRAG环境

如果您想自己构建GraphRAG环境：

1. **创建GraphRAG虚拟环境**
```bash
cd llm_backend/app/graphrag
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装GraphRAG依赖
pip install graphrag pandas numpy pyarrow
```

2. **下载静态资源**
```bash
# 仅下载 static_assets.tar.gz
tar -xzf static_assets.tar.gz -C llm_backend/static/
```

## 🔧 故障排除

### GraphRAG相关问题

**问题**: GraphRAG功能无法使用
**解决方案**: 
1. 确保已正确解压 `graphrag_venv.tar.gz`
2. 检查路径 `llm_backend/app/graphrag/venv/` 是否存在
3. 在 `.env` 中正确配置GraphRAG相关变量

### 静态资源问题

**问题**: 前端背景动画不显示
**解决方案**:
1. 确保已解压 `static_assets.tar.gz`
2. 检查文件 `llm_backend/static/assets/bg-T0alJtuh.gif` 是否存在
3. 重启服务器

### 网络下载问题

**问题**: 大文件下载失败
**解决方案**:
1. 使用下载工具（如wget、curl）进行断点续传
2. 检查网络连接稳定性
3. 联系项目维护者获取备用下载链接

## 📞 获取帮助

如果在安装过程中遇到问题：

1. **查看Issues**: [GitHub Issues](https://github.com/yourusername/gbc-madai/issues)
2. **创建新Issue**: 描述您遇到的具体问题
3. **讨论区**: [GitHub Discussions](https://github.com/yourusername/gbc-madai/discussions)

## 📝 文件校验

为确保下载文件完整性，您可以验证文件哈希：

```bash
# GraphRAG虚拟环境校验
sha256sum graphrag_venv.tar.gz
# 期望值: d7ceccf1ea83ce2781355e6616151e2acaddc2691b599279f0082685a60cf7d7

# 静态资源校验
sha256sum static_assets.tar.gz
# 期望值: 302ab4dc6127d3138f692968bc7290b4831c69a92739ad66dc1667d171d72c7f
```

### 文件信息
- **graphrag_venv.tar.gz**: 377MB (GraphRAG虚拟环境)
- **static_assets.tar.gz**: 131MB (前端静态资源)
- **总计**: 508MB

---

**注意**: 这些大文件包是可选的。核心功能可以在不下载这些文件的情况下正常运行，只是会缺少GraphRAG功能和部分UI动画效果。
