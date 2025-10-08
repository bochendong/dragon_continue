#!/bin/bash
# 快速部署到Vercel

set -e

echo "🚀 开始部署到Vercel..."
echo "=========================================="
echo ""

# 检查是否安装了vercel cli
if ! command -v vercel &> /dev/null; then
    echo "📦 安装Vercel CLI..."
    npm install -g vercel
fi

# 检查是否登录
echo "🔐 检查登录状态..."
if ! vercel whoami &> /dev/null; then
    echo "请先登录Vercel:"
    vercel login
fi

# 构建前端
echo ""
echo "🔨 构建前端..."
npm run build

# 部署
echo ""
echo "🚀 部署到Vercel..."
vercel --prod

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo ""
echo "📝 下一步："
echo "  1. 访问Vercel Dashboard查看部署状态"
echo "  2. 配置自定义域名（可选）"
echo "  3. 测试应用功能"
echo ""

