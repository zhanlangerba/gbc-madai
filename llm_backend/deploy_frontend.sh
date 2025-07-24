#!/bin/bash

# 前端二次元风格界面部署脚本
# 用于将Vue前端构建文件部署到FastAPI后端的静态目录

set -e  # 遇到错误立即退出

echo "🌸 开始部署二次元风格前端界面..."

# 定义路径
FRONTEND_DIR="/root/Assistgen/Assistgen/gbc_madai_web"
BACKEND_DIR="/root/Assistgen/Assistgen/gbc_madai_project/llm_backend"
STATIC_DIR="$BACKEND_DIR/static"

# 检查前端目录是否存在
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ 错误: 前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

# 检查后端目录是否存在
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ 错误: 后端目录不存在: $BACKEND_DIR"
    exit 1
fi

echo "📁 前端目录: $FRONTEND_DIR"
echo "📁 后端目录: $BACKEND_DIR"

# 进入前端目录
cd "$FRONTEND_DIR"

echo "🔧 安装前端依赖..."
npm install

echo "🏗️ 构建前端项目..."
npm run build

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo "❌ 错误: 前端构建失败，dist目录不存在"
    exit 1
fi

echo "✅ 前端构建成功"

# 创建后端静态目录
echo "📂 创建静态文件目录..."
mkdir -p "$STATIC_DIR"

# 清理旧的静态文件
echo "🧹 清理旧的静态文件..."
rm -rf "$STATIC_DIR"/*

# 复制新的构建文件
echo "📋 复制构建文件到后端..."
cp -r dist/* "$STATIC_DIR/"

# 验证文件复制
if [ ! -f "$STATIC_DIR/index.html" ]; then
    echo "❌ 错误: 文件复制失败，index.html不存在"
    exit 1
fi

echo "✅ 文件复制成功"

# 显示部署的文件
echo "📊 部署的文件列表:"
ls -la "$STATIC_DIR/"

echo ""
echo "📊 资源文件:"
ls -la "$STATIC_DIR/assets/" | head -10

# 检查图片资源
echo ""
echo "🖼️ 二次元图片资源:"
find "$STATIC_DIR/assets/" -name "*.png" -o -name "*.jpg" -o -name "*.gif" | head -5

echo ""
echo "🎉 部署完成！"
echo ""
echo "📝 部署总结:"
echo "   ✅ 前端构建: 成功"
echo "   ✅ 文件复制: 成功"
echo "   ✅ 静态资源: 已部署到 $STATIC_DIR"
echo "   ✅ 二次元素材: 已集成"
echo ""
echo "🚀 现在可以启动后端服务器:"
echo "   cd $BACKEND_DIR"
echo "   python run.py"
echo ""
echo "🌐 访问地址: http://117.72.186.67:8000"
echo ""
echo "🎨 二次元风格特性:"
echo "   • 渐变背景和毛玻璃效果"
echo "   • Q版角色装饰"
echo "   • GIF动画表情"
echo "   • 粉色系配色方案"
echo "   • 流畅的CSS动画"

# 前端二次元风格界面部署脚本
# 用于将Vue前端构建文件部署到FastAPI后端的静态目录

set -e  # 遇到错误立即退出

echo "🌸 开始部署二次元风格前端界面..."

# 定义路径
FRONTEND_DIR="/root/Assistgen/Assistgen/gbc_madai_web"
BACKEND_DIR="/root/Assistgen/Assistgen/gbc_madai_project/llm_backend"
STATIC_DIR="$BACKEND_DIR/static"
DIST_DIR="$STATIC_DIR/dist"

# 检查前端目录是否存在
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ 错误: 前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

# 检查后端目录是否存在
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ 错误: 后端目录不存在: $BACKEND_DIR"
    exit 1
fi

echo "📁 前端目录: $FRONTEND_DIR"
echo "📁 后端目录: $BACKEND_DIR"

# 进入前端目录
cd "$FRONTEND_DIR"

echo "🔧 安装前端依赖..."
npm install

echo "🏗️ 构建前端项目..."
npm run build

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo "❌ 错误: 前端构建失败，dist目录不存在"
    exit 1
fi

echo "✅ 前端构建成功"

# 创建后端静态目录
echo "📂 创建静态文件目录..."
mkdir -p "$DIST_DIR"

# 清理旧的静态文件
echo "🧹 清理旧的静态文件..."
rm -rf "$DIST_DIR"/*

# 复制新的构建文件
echo "📋 复制构建文件到后端..."
cp -r dist/* "$DIST_DIR/"

# 验证文件复制
if [ ! -f "$DIST_DIR/index.html" ]; then
    echo "❌ 错误: 文件复制失败，index.html不存在"
    exit 1
fi

echo "✅ 文件复制成功"

# 显示部署的文件
echo "📊 部署的文件列表:"
ls -la "$DIST_DIR/"

echo ""
echo "📊 资源文件:"
ls -la "$DIST_DIR/assets/" | head -10

# 检查图片资源
echo ""
echo "🖼️ 二次元图片资源:"
find "$DIST_DIR/assets/" -name "*.png" -o -name "*.jpg" -o -name "*.gif" | head -5

echo ""
echo "🎉 部署完成！"
echo ""
echo "📝 部署总结:"
echo "   ✅ 前端构建: 成功"
echo "   ✅ 文件复制: 成功"
echo "   ✅ 静态资源: 已部署到 $DIST_DIR"
echo "   ✅ 二次元素材: 已集成"
echo ""
echo "🚀 现在可以启动后端服务器:"
echo "   cd $BACKEND_DIR"
echo "   python run.py"
echo ""
echo "🌐 访问地址: http://117.72.186.67:8000"
echo ""
echo "🎨 二次元风格特性:"
echo "   • 渐变背景和毛玻璃效果"
echo "   • Q版角色装饰"
echo "   • GIF动画表情"
echo "   • 粉色系配色方案"
echo "   • 流畅的CSS动画"
