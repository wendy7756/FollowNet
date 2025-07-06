# 🚀 FollowNet Installation Guide

## System Requirements

- **Python**: 3.11+
- **Node.js**: 18+
- **Memory**: 8GB+ recommended
- **Operating System**: macOS, Linux, Windows

## 📦 Quick Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd FollowNet
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Install Playwright Browser
```bash
playwright install chromium
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
# or use pnpm
pnpm install
```

## 🔧 Dependencies Overview

### Backend Dependencies (requirements.txt)
```txt
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
playwright==1.40.0        # Browser automation
python-multipart==0.0.6   # File upload support
aiofiles==23.2.1          # Async file operations
pydantic==2.5.0           # Data validation
aiohttp==3.12.13          # HTTP client
```

### Frontend Dependencies (package.json)
```json
{
  "dependencies": {
    "@radix-ui/react-slot": "^1.2.3",
    "@tanstack/react-table": "^8.21.3",
    "axios": "^1.10.0",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.523.0",
    "next": "^15.3.4",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "tailwind-merge": "^3.3.1"
  }
}
```

## 🚀 Starting Services

### Method 1: Start Separately (Recommended)

#### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
python main.py
```
Backend will run on: http://localhost:8000

#### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Frontend will run on: http://localhost:3000 (or next available port)

### Method 2: Using Start Script
```bash
# Create start script
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting FollowNet..."

# Start backend
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ FollowNet started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x start.sh
./start.sh
```

## 🔍 Installation Verification

### 1. Check Backend
```bash
curl http://localhost:8000/health
# Should return: {"detail":"Not Found"} (this is normal, means server is running)
```

### 2. Check Frontend
Visit http://localhost:3000, you should see the FollowNet interface

### 3. Test Functionality
1. Enter a test URL: `https://github.com/octocat`
2. Check if platform detection works
3. Click "Submit" to start scraping
4. Verify data extraction and CSV download

## 🛠️ Troubleshooting

### Common Issues

**Q1: `command not found: python3`**
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# Windows
# Download and install from python.org
```

**Q2: `command not found: npm`**
```bash
# macOS
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# Download and install from nodejs.org
```

**Q3: `playwright install` fails**
```bash
# Install browser manually
python -m playwright install chromium

# If still fails, try
python -m playwright install-deps
python -m playwright install chromium
```

**Q4: Port already in use**
```bash
# Find process using port
lsof -ti:8000  # Backend port
lsof -ti:3000  # Frontend port

# Kill process
kill -9 <PID>

# Or change port
# Backend: modify port in main.py
# Frontend: use npm run dev -- -p 3001
```

**Q5: Package installation fails**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules
npm install

# For Python packages
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Q6: Playwright browser download fails**
```bash
# Set proxy if needed
export HTTPS_PROXY=http://proxy.example.com:8080

# Install with specific browser
playwright install chromium --with-deps

# Check installation
playwright install-deps
```

### Performance Issues

**Memory shortage**
```bash
# Reduce concurrent processing
# In optimized scrapers, modify:
max_concurrent = 3    # Reduce from higher values
batch_size = 10       # Reduce batch size
```

**Network timeouts**
```bash
# Increase timeout values
# In scrapers, modify:
timeout = 30000  # Increase from 15000
```

## 📊 Performance Testing

### Basic Test
```bash
cd backend
python -c "
import asyncio
from scrapers.github_two_stage import GitHubTwoStageOptimized
async def test():
    scraper = GitHubTwoStageOptimized()
    result = await scraper.scrape_followers('octocat', max_pages=1)
    print(f'Test successful: {len(result)} users scraped')
asyncio.run(test())
"
```

### Expected Performance
- **Small scale** (100 users): 1-2 minutes
- **Medium scale** (500 users): 3-5 minutes  
- **Large scale** (1000 users): 5-8 minutes

## 🔄 Update Guide

### Update Backend Dependencies
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Update Frontend Dependencies
```bash
cd frontend
npm update
# or
pnpm update
```

### Update Playwright
```bash
cd backend
source venv/bin/activate
playwright install chromium
```

## 🎯 Next Steps

After installation, you can:

1. **Read functionality docs**: Check the main README
2. **View usage examples**: `DEMO.md`
3. **Learn deployment**: `DEPLOYMENT.md`
4. **Contribute**: Check source code and contribution guidelines

## 📞 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review GitHub Issues
3. Run diagnostic tests
4. Check backend and frontend console output
5. Verify all dependencies are correctly installed

Happy coding! 🎉 