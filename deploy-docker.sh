#!/bin/bash
# 使用Docker部署

set -e

echo "🐳 使用Docker部署龙族续写项目"
echo "=========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装！"
    echo "请访问 https://docs.docker.com/get-docker/ 安装Docker"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装！"
    echo "请访问 https://docs.docker.com/compose/install/ 安装Docker Compose"
    exit 1
fi

# 检查环境变量
if [ ! -f .env ]; then
    echo "⚠️ 未找到.env文件，创建示例文件..."
    cat > .env << EOF
# OpenAI API Key
OPENAI_API_KEY=your-api-key-here

# 环境
NODE_ENV=production
EOF
    echo "✅ 已创建.env文件，请编辑并填入你的API Key"
    echo ""
    read -p "按回车继续..."
fi

# 构建镜像
echo ""
echo "🔨 构建Docker镜像..."
docker-compose build

# 启动服务
echo ""
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查状态
echo ""
echo "📊 服务状态："
docker-compose ps

# 查看日志
echo ""
echo "📝 服务日志（最后20行）："
docker-compose logs --tail=20

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo ""
echo "📱 访问地址："
echo "  http://localhost:3000"
echo ""
echo "🛠️ 常用命令："
echo "  查看日志:   docker-compose logs -f"
echo "  重启服务:   docker-compose restart"
echo "  停止服务:   docker-compose stop"
echo "  删除服务:   docker-compose down"
echo "  查看状态:   docker-compose ps"
echo ""

