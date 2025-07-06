# FollowNet Deployment Guide

## 🚀 Deployment Architecture

- **Backend**: Railway (Supports Playwright + FastAPI)
- **Frontend**: Vercel (Static hosting + Serverless functions)

## 📋 Prerequisites

### Environment Requirements
- Node.js 18+ (Frontend)
- Python 3.11+ (Backend)
- Git account
- Railway account
- Vercel account

## 🔧 Backend Deployment (Railway)

### 1. Prepare Railway Deployment

1. Login to [Railway](https://railway.app)
2. Create a new project
3. Connect your GitHub repository

### 2. Configure Environment Variables

Add the following environment variables in Railway project settings:

```bash
PYTHON_VERSION=3.11
PORT=8000
```

### 3. Deployment Configuration

Railway will automatically detect the Python project and install dependencies. Make sure the `railway.json` file is in the root directory:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd backend && pip install -r requirements.txt && playwright install chromium",
    "watchPatterns": ["backend/**"]
  },
  "deploy": {
    "startCommand": "cd backend && python main.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 4. Get Deployment URL

After successful deployment, Railway will provide a URL like:
```
https://your-app-name.railway.app
```

Record this URL, as it will be needed for the frontend configuration.

## 🌐 Frontend Deployment (Vercel)

### 1. Update API Configuration

In `frontend/next.config.js`, update the production API URL:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: process.env.NODE_ENV === 'production' 
        ? 'https://your-railway-app.railway.app/api/:path*'  // Replace with your Railway URL
        : 'http://localhost:8000/api/:path*',
    },
  ];
},
```

### 2. Deploy to Vercel

#### Method 1: Via Vercel Dashboard

1. Login to [Vercel](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

#### Method 2: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

### 3. Environment Variables Configuration

Add the following environment variables in Vercel project settings:

```bash
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

### 4. Custom Domain (Optional)

1. In Vercel project settings, click "Domains"
2. Add your custom domain
3. Configure DNS records as instructed

## 🔄 CORS Configuration

Ensure backend properly configures CORS to allow frontend access:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-vercel-app.vercel.app",  # Vercel
        "https://your-custom-domain.com"  # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## ⚙️ Environment-specific Configuration

### Development Environment
```bash
# Frontend
cd frontend
npm run dev

# Backend
cd backend
python main.py
```

### Production Environment

Frontend automatically deploys to Vercel, backend deploys to Railway.

## 🛠️ Deployment Verification

### 1. Check Backend Health

Visit: `https://your-railway-app.railway.app/`

Should return:
```json
{"message": "FollowNet API is running"}
```

### 2. Check Frontend

Visit your Vercel URL and verify:
- Page loads correctly
- Platform detection works
- API calls succeed

### 3. Test Complete Workflow

1. Enter a GitHub URL
2. Check platform detection
3. Click Submit button
4. Verify data scraping and CSV download functionality

## 🚨 Common Issues

### Railway Deployment Issues

**Q: Playwright installation fails**
```bash
# In Railway, ensure correct build command
playwright install chromium
```

**Q: Out of memory**
- Upgrade Railway plan
- Optimize scraper memory usage

### Vercel Deployment Issues

**Q: API calls fail**
- Check CORS configuration
- Verify API URL is correct
- Check _headers file configuration

**Q: Build fails**
```bash
# Ensure package.json has correct scripts
"scripts": {
  "build": "next build",
  "start": "next start"
}
```

## 🔧 Alternative Deployment: Render

If you prefer Render for backend deployment:

### Render Configuration
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt && playwright install chromium`
- **Start Command**: `python main.py`
- **Environment Variables**: `PYTHON_VERSION=3.11.7`, `PORT=8000`

This configuration has been tested and works successfully.

## 📊 Performance Optimization

### Backend Optimization
- Enable caching
- Configure CDN
- Optimize database queries

### Frontend Optimization
- Enable Vercel caching
- Compress static assets
- Use Vercel Image optimization

## 🔒 Security Considerations

### API Security
- Implement rate limiting
- Add API key authentication
- Configure firewall rules

### Frontend Security
- Enable HSTS
- Configure CSP headers
- Use HTTPS

## 📈 Monitoring and Logging

### Railway Monitoring
- Use Railway built-in monitoring
- Configure error alerts
- View application logs

### Vercel Analytics
- Enable Web Analytics
- Monitor performance metrics
- View access statistics

## 🔄 CI/CD Pipeline

### Automatic Deployment

1. **Code Push** → GitHub
2. **Railway Auto-build** → Backend deployment
3. **Vercel Auto-build** → Frontend deployment

### Branch Strategy

- `main` → Production environment
- `staging` → Staging environment
- `dev` → Development environment

## 📞 Support

If you encounter deployment issues:

1. Check build logs
2. Verify environment variable configuration
3. Confirm dependency version compatibility
4. Review official documentation:
   - [Railway Docs](https://docs.railway.app)
   - [Vercel Docs](https://vercel.com/docs)

---

🎉 Deployment complete! Your FollowNet application is now accessible globally. 