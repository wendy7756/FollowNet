# 🚀 FollowNet 安装指南 (无限制爬取版本)

## 系统要求

- **Python**: 3.9+
- **Node.js**: 18+
- **内存**: 推荐8GB+
- **操作系统**: macOS, Linux, Windows

## 📦 快速安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd FollowNet
```

### 2. 后端设置

#### 创建虚拟环境
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows
```

#### 安装Python依赖
```bash
pip install -r requirements.txt
```

#### 安装Playwright浏览器
```bash
playwright install chromium
```

### 3. 前端设置
```bash
cd ../frontend
npm install
# 或者使用pnpm
pnpm install
```

## 🔧 依赖说明

### 后端依赖 (requirements.txt)
```txt
fastapi==0.104.1          # Web框架
uvicorn==0.24.0           # ASGI服务器
playwright==1.40.0        # 浏览器自动化
python-multipart==0.0.6   # 文件上传支持
aiofiles==23.2.1          # 异步文件操作
pydantic==2.5.0           # 数据验证
aiohttp==3.12.13          # HTTP客户端 (新增)
```

### 前端依赖 (package.json)
```json
{
  "dependencies": {
    "@radix-ui/react-slot": "^1.2.3",
    "@tanstack/react-table": "^8.21.3",
    "axios": "^1.10.0",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.523.0",      // 图标库 (包含Settings图标)
    "next": "^15.3.4",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "tailwind-merge": "^3.3.1"
  }
}
```

## 🚀 启动服务

### 方法1: 分别启动 (推荐)

#### 启动后端 (终端1)
```bash
cd backend
source venv/bin/activate
python main.py
```
后端将运行在: http://localhost:8000

#### 启动前端 (终端2)
```bash
cd frontend
npm run dev
```
前端将运行在: http://localhost:3000 (或下一个可用端口)

### 方法2: 使用脚本启动
```bash
# 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting FollowNet with Unlimited Scraping..."

# 启动后端
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ FollowNet started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop all services"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x start.sh
./start.sh
```

## 🔍 验证安装

### 1. 检查后端
```bash
curl http://localhost:8000/health
# 应该返回: {"detail":"Not Found"} (这是正常的，说明服务器在运行)
```

### 2. 检查前端
访问 http://localhost:3000，应该看到FollowNet界面

### 3. 测试无限制功能
1. 在前端勾选 "Unlimited Mode"
2. 设置 "Maximum Users to Scrape" 为 500
3. 输入测试URL: `https://github.com/octocat`
4. 点击 "Start" 开始测试

## 🛠️ 故障排除

### 常见问题

**Q1: `command not found: python3`**
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# Windows
# 从 python.org 下载安装
```

**Q2: `command not found: npm`**
```bash
# macOS
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# 从 nodejs.org 下载安装
```

**Q3: `playwright install` 失败**
```bash
# 手动安装浏览器
python -m playwright install chromium

# 如果还是失败，尝试
python -m playwright install-deps
python -m playwright install chromium
```

**Q4: 端口被占用**
```bash
# 查找占用端口的进程
lsof -ti:8000  # 后端端口
lsof -ti:3000  # 前端端口

# 杀死进程
kill -9 <PID>

# 或者修改端口
# 后端: 修改 main.py 中的端口
# 前端: 使用 npm run dev -- -p 3001
```

**Q5: 无限制模式不工作**
```bash
# 检查后端日志
cd backend
source venv/bin/activate
python main.py

# 查看是否有错误信息
# 确保看到: "🚀 Starting unlimited scraping mode"
```

**Q6: 前端Advanced Settings不显示**
```bash
# 检查前端依赖
cd frontend
npm install lucide-react

# 重启前端
npm run dev
```

### 性能优化

**内存不足**
```bash
# 减少并发数
# 在 unlimited_followers_scraper.py 中修改:
max_concurrent = 10  # 从20减少到10
batch_size = 25      # 从50减少到25
```

**网络超时**
```bash
# 增加超时时间
# 在 unlimited_followers_scraper.py 中修改:
timeout = 30000  # 从15000增加到30000
```

## 📊 性能测试

### 基准测试
```bash
cd backend
python test_unlimited.py
```

### 预期结果
- **小规模** (500用户): 2-3分钟
- **中规模** (1000用户): 3-5分钟  
- **大规模** (2000用户): 5-8分钟

## 🔄 更新指南

### 更新后端依赖
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 更新前端依赖
```bash
cd frontend
npm update
# 或
pnpm update
```

### 更新Playwright
```bash
cd backend
source venv/bin/activate
playwright install chromium
```

## 🎯 下一步

安装完成后，你可以：

1. **阅读功能文档**: `UNLIMITED_SCRAPING.md`
2. **查看使用示例**: `DEMO.md`
3. **了解部署方案**: `DEPLOYMENT.md`
4. **参与开发**: 查看源码和贡献指南

## 📞 获取帮助

如果遇到问题：

1. 检查本文档的故障排除部分
2. 查看GitHub Issues
3. 运行测试脚本进行诊断
4. 检查后端和前端的控制台输出

祝你使用愉快！🎉 