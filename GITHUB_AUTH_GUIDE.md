# GitHub认证问题解决指南

## 🚨 问题描述
GitHub在2021年8月13日停止了密码认证，现在需要使用Personal Access Token (PAT)。

## 🔐 解决方案

### 方法一：使用自动化脚本（推荐）

```bash
chmod +x setup_github_auth.sh
./setup_github_auth.sh
```

### 方法二：手动设置

#### 步骤1：创建Personal Access Token

1. **访问GitHub设置页面**：
   - 登录GitHub → 右上角头像 → Settings
   - 或直接访问：https://github.com/settings/tokens

2. **生成新Token**：
   - 点击 "Generate new token" → "Generate new token (classic)"
   - **Note**: 填写 "GBC MedAI Project"
   - **Expiration**: 选择 "90 days" 或 "No expiration"
   - **Select scopes**: 勾选以下权限
     - ✅ **repo** (完整仓库访问权限)
     - ✅ **workflow** (如果需要GitHub Actions)

3. **复制Token**：
   - 点击 "Generate token"
   - 复制生成的token（格式：`ghp_xxxxxxxxxxxxxxxxxxxx`）
   - ⚠️ **重要**：Token只显示一次，请立即保存！

#### 步骤2：配置Git认证

```bash
# 方式1：更新远程URL（推荐）
git remote set-url origin https://YOUR_TOKEN@github.com/zhanlangerba/gbc-madai.git

# 方式2：使用Git凭据管理器
git config --global credential.helper store
```

#### 步骤3：推送代码

```bash
# 推送主分支
git push -u origin main

# 创建并推送标签
git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"
git push origin v1.0.0
```

## 🔧 快速命令

如果您已经有了Personal Access Token，可以直接运行：

```bash
# 替换 YOUR_TOKEN 为您的实际token
TOKEN="ghp_your_actual_token_here"
git remote set-url origin "https://$TOKEN@github.com/zhanlangerba/gbc-madai.git"
git push -u origin main
git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"
git push origin v1.0.0
```

## 🛠 替代方案

### 方案A：SSH密钥认证

1. **生成SSH密钥**：
```bash
ssh-keygen -t rsa -b 4096 -C "3397316724@qq.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
```

2. **添加公钥到GitHub**：
```bash
cat ~/.ssh/id_rsa.pub
# 复制输出，在GitHub → Settings → SSH and GPG keys 中添加
```

3. **更改远程URL**：
```bash
git remote set-url origin git@github.com:zhanlangerba/gbc-madai.git
git push -u origin main
```

### 方案B：GitHub CLI

1. **安装GitHub CLI**：
```bash
# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

2. **认证并推送**：
```bash
gh auth login
git push -u origin main
```

## 🔒 安全最佳实践

### Token安全
- ✅ 设置合理的过期时间
- ✅ 只授予必要的权限
- ✅ 定期轮换Token
- ✅ 不要在代码中硬编码Token
- ❌ 不要分享Token给他人

### 环境变量方式
```bash
# 设置环境变量
export GITHUB_TOKEN="ghp_your_token_here"

# 使用环境变量
git remote set-url origin "https://$GITHUB_TOKEN@github.com/zhanlangerba/gbc-madai.git"
```

## 🆘 常见问题

### Q: Token格式错误
**A**: 确保Token以 `ghp_` 开头，总长度为40个字符

### Q: 权限不足
**A**: 检查Token是否包含 `repo` 权限

### Q: Token过期
**A**: 重新生成新的Token并更新配置

### Q: 网络连接问题
**A**: 检查防火墙设置，尝试使用代理

## 📞 获取帮助

如果仍然遇到问题：

1. **检查GitHub状态**：https://www.githubstatus.com/
2. **查看GitHub文档**：https://docs.github.com/en/authentication
3. **联系GitHub支持**：https://support.github.com/

---

**选择最适合您的认证方式，推荐使用Personal Access Token！** 🚀
