#!/bin/bash

# GitHub认证设置脚本
# 帮助设置Personal Access Token认证

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

echo "🔐 GitHub认证设置向导"
echo "===================="
echo ""

print_step "1. 创建Personal Access Token"
echo ""
echo "请按照以下步骤创建GitHub Personal Access Token："
echo ""
echo "1. 访问: https://github.com/settings/tokens"
echo "2. 点击 'Generate new token' → 'Generate new token (classic)'"
echo "3. 填写Token描述: 'GBC MedAI Project'"
echo "4. 选择过期时间: 建议选择 '90 days' 或 'No expiration'"
echo "5. 勾选权限范围:"
echo "   ✅ repo (完整仓库访问权限)"
echo "   ✅ workflow (如果需要GitHub Actions)"
echo "6. 点击 'Generate token'"
echo "7. 复制生成的token (格式类似: ghp_xxxxxxxxxxxxxxxxxxxx)"
echo ""
print_warning "⚠️  Token只会显示一次，请务必复制保存！"
echo ""

read -p "按Enter键继续，当您已经获得了Personal Access Token..."

print_step "2. 配置Git认证"
echo ""
read -p "请粘贴您的Personal Access Token: " github_token

if [ -z "$github_token" ]; then
    print_error "Token不能为空"
    exit 1
fi

# 验证token格式
if [[ ! $github_token =~ ^ghp_[a-zA-Z0-9]{36}$ ]]; then
    print_warning "Token格式可能不正确，但继续尝试..."
fi

print_step "3. 更新远程仓库URL"
# 将token嵌入到URL中
git remote set-url origin "https://$github_token@github.com/zhanlangerba/gbc-madai.git"

print_message "✅ 远程仓库URL已更新"

print_step "4. 测试连接"
if git ls-remote origin > /dev/null 2>&1; then
    print_message "✅ GitHub连接测试成功！"
else
    print_error "❌ 连接测试失败，请检查Token是否正确"
    exit 1
fi

print_step "5. 推送代码"
echo ""
print_message "现在尝试推送代码到GitHub..."

if git push -u origin main; then
    print_message "🎉 代码推送成功！"
    
    print_step "6. 创建版本标签"
    git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"
    git push origin v1.0.0
    print_message "✅ 版本标签创建成功！"
    
    echo ""
    echo "🎉 项目发布完成！"
    echo "=================="
    echo ""
    echo "📋 发布信息:"
    echo "   仓库地址: https://github.com/zhanlangerba/gbc-madai"
    echo "   版本标签: v1.0.0"
    echo "   项目大小: 234MB"
    echo ""
    echo "🔗 下一步:"
    echo "1. 访问GitHub仓库页面"
    echo "2. 添加项目描述和Topics标签"
    echo "3. 上传大文件到网盘"
    echo "4. 更新LARGE_FILES_README.md中的下载链接"
    echo ""
    
else
    print_error "❌ 推送失败"
    echo ""
    echo "💡 可能的解决方案:"
    echo "1. 检查Token权限是否包含 'repo'"
    echo "2. 确认Token没有过期"
    echo "3. 检查网络连接"
    echo "4. 尝试重新生成Token"
fi

print_step "7. 安全提醒"
echo ""
print_warning "🔒 安全提醒:"
echo "- Token已保存在Git配置中，请妥善保管"
echo "- 不要将Token分享给他人"
echo "- 定期更新Token"
echo "- 如果Token泄露，立即在GitHub上撤销"
