# 龙族续写项目 - 部署指南

本文档介绍如何将项目部署到生产环境。

---

## 🎯 部署选项

### 选项对比

| 部署方式 | 难度 | 成本 | 适用场景 |
|---------|------|------|---------|
| **Vercel** | ⭐ 简单 | 免费 | 前端展示（只读） |
| **GitHub Pages** | ⭐ 简单 | 免费 | 静态站点 |
| **Railway** | ⭐⭐ 中等 | $5/月起 | 全栈应用 |
| **AWS/阿里云** | ⭐⭐⭐ 复杂 | 按量计费 | 生产环境 |
| **Docker** | ⭐⭐ 中等 | 服务器成本 | 自托管 |

---

## 📦 方案1：Vercel部署（推荐-前端）

**适用场景**：只部署前端阅读界面，章节静态展示

### 步骤

#### 1. 准备项目

```bash
# 构建前端
npm run build

# 测试构建结果
npm install -g serve
serve -s build
```

#### 2. 在Vercel上部署

**方式A：通过Git**

1. 将代码推送到GitHub
2. 访问 [vercel.com](https://vercel.com)
3. 点击"Import Project"
4. 选择你的GitHub仓库
5. 配置：
   - Framework Preset: `Create React App`
   - Build Command: `npm run build`
   - Output Directory: `build`
6. 点击"Deploy"

**方式B：通过CLI**

```bash
# 安装Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel

# 生产环境部署
vercel --prod
```

#### 3. 配置文件（vercel.json）

创建 `vercel.json`：

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/chapters_2000_words/(.*)",
      "dest": "/chapters_2000_words/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### 限制

- ❌ 无法运行Python后端
- ❌ 无法实时生成新章节
- ✅ 可以展示已生成的章节
- ✅ 完全免费

---

## 📦 方案2：Railway部署（推荐-全栈）

**适用场景**：部署完整应用，包含AI生成功能

### 步骤

#### 1. 准备Docker配置

创建 `Dockerfile`：

```dockerfile
# 多阶段构建

# Stage 1: 构建前端
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Python后端 + 前端静态文件
FROM python:3.11-slim

# 安装依赖
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制Python代码
COPY agents ./agents
COPY chapters_2000_words ./chapters_2000_words
COPY 《龙族Ⅰ火之晨曦》_readable.txt .

# 复制前端构建结果
COPY --from=frontend-builder /app/build ./build

# 安装serve来托管前端
RUN npm install -g serve

# 暴露端口
EXPOSE 3000 8000

# 启动脚本
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
```

创建 `start.sh`：

```bash
#!/bin/bash

# 启动前端
serve -s build -l 3000 &

# 等待前端启动
sleep 2

# 保持容器运行
tail -f /dev/null
```

创建 `.dockerignore`：

```
node_modules
build
agents_venv
__pycache__
*.pyc
.git
.env
*.log
```

#### 2. 在Railway部署

1. 访问 [railway.app](https://railway.app)
2. 使用GitHub登录
3. 点击"New Project"
4. 选择"Deploy from GitHub repo"
5. 选择你的仓库
6. 配置环境变量：
   ```
   OPENAI_API_KEY=your-api-key-here
   PORT=3000
   ```
7. Railway会自动检测Dockerfile并部署

#### 3. 配置railway.json（可选）

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "./start.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 成本

- 免费额度：$5/月
- 付费：$5/月起
- 按实际使用计费

---

## 📦 方案3：阿里云/腾讯云（生产环境）

**适用场景**：完整生产环境，高可用性

### 架构

```
用户
  ↓
阿里云SLB（负载均衡）
  ↓
ECS实例（Docker容器）
  ├─ Nginx（反向代理）
  ├─ React前端（静态文件）
  └─ Python后端（API服务）
  ↓
RDS数据库（MySQL/PostgreSQL）
OSS对象存储（章节文件）
```

### 步骤

#### 1. 购买服务器

- **ECS**：2核4G起步（约¥100/月）
- **带宽**：5M起步
- **系统**：Ubuntu 22.04 LTS

#### 2. 安装Docker

```bash
# 连接到服务器
ssh root@your-server-ip

# 安装Docker
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

#### 3. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  # 前端 + 静态文件服务
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "80:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./chapters_2000_words:/app/chapters_2000_words:ro
    restart: unless-stopped

  # Python后端（如需API）
  backend:
    build:
      context: ./agents
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./agents/database:/app/database
      - ./chapters_2000_words:/app/chapters_2000_words
    restart: unless-stopped

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

#### 4. 配置Nginx

创建 `nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # 前端
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # API（如果需要）
        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 章节文件
        location /chapters_2000_words/ {
            alias /app/chapters_2000_words/;
            autoindex off;
        }
    }
}
```

#### 5. 部署

```bash
# 克隆代码
git clone <your-repo-url>
cd dragon_continue

# 配置环境变量
echo "OPENAI_API_KEY=your-key" > .env

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 更新代码
git pull
docker-compose up -d --build
```

#### 6. 配置域名

1. 在域名提供商处添加A记录指向服务器IP
2. 配置SSL证书（使用Let's Encrypt）：

```bash
# 安装certbot
apt install certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

### 成本估算

- ECS 2核4G：¥100/月
- 带宽 5M：¥50/月
- 域名：¥50/年
- SSL证书：免费（Let's Encrypt）
- **总计**：约¥150/月

---

## 📦 方案4：GitHub Pages（静态展示）

**适用场景**：展示已生成的章节，不需要生成功能

### 步骤

#### 1. 配置package.json

添加homepage：

```json
{
  "homepage": "https://yourusername.github.io/dragon_continue",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

#### 2. 安装gh-pages

```bash
npm install --save-dev gh-pages
```

#### 3. 部署

```bash
npm run deploy
```

#### 4. 配置GitHub仓库

1. 进入仓库Settings
2. 找到Pages选项
3. Source选择`gh-pages`分支
4. 保存

### 限制

- ❌ 无后端功能
- ❌ 无法生成新章节
- ✅ 完全免费
- ✅ 可以展示静态内容

---

## 🔧 环境变量配置

### 必需的环境变量

```bash
# OpenAI API Key（必需）
OPENAI_API_KEY=sk-xxx

# 环境（可选）
NODE_ENV=production

# 端口（可选）
PORT=3000
```

### 在不同平台配置

**Vercel**：
- Dashboard → Settings → Environment Variables

**Railway**：
- Project → Variables → New Variable

**Docker**：
- 使用 `.env` 文件或 `docker-compose.yml` 中的 `environment`

---

## 📋 部署前检查清单

### 代码准备

- [ ] 所有测试通过
- [ ] 移除调试代码
- [ ] 更新README
- [ ] 检查.gitignore
- [ ] 配置环境变量

### 安全检查

- [ ] API Key不在代码中
- [ ] 使用环境变量
- [ ] 配置HTTPS
- [ ] 添加rate limiting（如需API）
- [ ] 数据库备份策略

### 性能优化

- [ ] 前端代码压缩（`npm run build`）
- [ ] 图片优化
- [ ] 启用CDN（可选）
- [ ] 配置缓存策略

### 监控

- [ ] 配置日志收集
- [ ] 设置错误监控
- [ ] 配置性能监控
- [ ] 设置告警

---

## 🔄 CI/CD配置

### GitHub Actions自动部署

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm install
      
    - name: Build
      run: npm run build
      
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        working-directory: ./
```

---

## 📊 部署后验证

### 功能测试

```bash
# 测试前端
curl https://your-domain.com

# 测试章节加载
curl https://your-domain.com/chapters_2000_words/001_楔子：白帝城.txt

# 测试API（如果有）
curl https://your-domain.com/api/health
```

### 性能测试

```bash
# 使用Lighthouse
npm install -g lighthouse
lighthouse https://your-domain.com

# 使用Apache Bench
ab -n 1000 -c 10 https://your-domain.com/
```

---

## 🆘 常见问题

### Q: 部署后页面空白？

**A**: 检查：
1. `package.json` 中的 `homepage` 配置
2. 路由配置是否正确
3. 浏览器控制台错误

### Q: 章节文件404？

**A**: 
1. 确认 `chapters_2000_words` 目录已上传
2. 检查Nginx配置
3. 检查文件路径和权限

### Q: API Key暴露？

**A**: 
1. 立即撤销旧Key
2. 生成新Key
3. 使用环境变量
4. 检查.gitignore

### Q: 部署成本太高？

**A**: 
1. 使用Vercel免费版（仅前端）
2. 使用Railway免费额度
3. 优化Docker镜像大小
4. 使用CDN减少带宽

---

## 🎯 推荐方案

### 个人项目/演示

**推荐**：Vercel
- ✅ 完全免费
- ✅ 自动HTTPS
- ✅ CDN加速
- ❌ 无后端

### 完整功能

**推荐**：Railway
- ✅ 支持全栈
- ✅ 自动HTTPS
- ✅ 简单易用
- 💰 $5/月起

### 生产环境

**推荐**：阿里云ECS + Docker
- ✅ 完全控制
- ✅ 高可用
- ✅ 可扩展
- 💰 约¥150/月

---

## 📞 技术支持

遇到部署问题？

1. 查看项目Issue
2. 阅读平台文档
3. 提交新Issue

---

**🚀 祝部署顺利！**

