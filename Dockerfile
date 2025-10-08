# 龙族续写项目 - Docker配置
# 多阶段构建：前端 + Python后端

# ==================== Stage 1: 构建前端 ====================
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY public ./public
COPY src ./src

# 构建
RUN npm run build

# ==================== Stage 2: Python环境 ====================
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制Python代码
COPY agents ./agents

# 复制章节文件
COPY chapters_2000_words ./chapters_2000_words

# 复制原著文本（如需提取角色信息）
COPY 《龙族Ⅰ火之晨曦》_readable.txt .

# 从Stage 1复制前端构建结果
COPY --from=frontend-builder /app/build ./build

# 安装Node.js（用于serve）
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g serve \
    && rm -rf /var/lib/apt/lists/*

# 创建启动脚本
COPY <<EOF /app/start.sh
#!/bin/bash
set -e

echo "🚀 启动龙族续写项目..."

# 启动前端（端口3000）
echo "📱 启动前端服务..."
serve -s build -l 3000 &

# 等待前端启动
sleep 3

echo "✅ 前端服务已启动: http://localhost:3000"

# 保持容器运行
tail -f /dev/null
EOF

RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# 启动
CMD ["/app/start.sh"]

