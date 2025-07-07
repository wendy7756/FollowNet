# FollowNet Deployment Guide

This guide covers deploying FollowNet to production using **Zeabur** for backend and **Vercel** for frontend.

## 🏗️ Architecture Overview

- **Backend**: FastAPI + Python → Deployed on Zeabur
- **Frontend**: Next.js → Deployed on Vercel
- **Database**: File-based storage (can be upgraded to PostgreSQL)

## 🚀 Backend Deployment (Zeabur)

### 1. Prerequisites

- Zeabur account ([zeabur.com](https://zeabur.com))
- GitHub repository with your code

### 2. Deploy to Zeabur

1. **Connect GitHub Repository**
   - Go to Zeabur dashboard
   - Click "Create Project"
   - Connect your GitHub repository
   - Select the repository containing FollowNet

2. **Configure Service**
   - Select "backend" as the root directory
   - Zeabur will automatically detect it's a Python project
   - Set the following environment variables:
     ```bash
     PORT=8000
     PYTHON_VERSION=3.11
     ```

3. **Build Configuration**
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Start Command: `python main.py`

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note your Zeabur app URL (e.g., `https://your-app.zeabur.app`)

### 3. Environment Variables

Configure these in Zeabur dashboard:

```bash
PORT=8000
PYTHON_VERSION=3.11
```

## 🌐 Frontend Deployment (Vercel)

### 1. Prerequisites

- Vercel account ([vercel.com](https://vercel.com))
- GitHub repository connected

### 2. Deploy to Vercel

#### Method 1: Via Vercel Dashboard

1. Go to Vercel dashboard
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
NEXT_PUBLIC_API_URL=https://your-zeabur-app.zeabur.app
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

Frontend automatically deploys to Vercel, backend deploys to Zeabur.

## 🛠️ Deployment Verification

### 1. Check Backend Health

Visit: `https://your-zeabur-app.zeabur.app/`

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

### Zeabur Deployment Issues

**Q: Playwright installation fails**
```bash
# In Zeabur, ensure correct build command
playwright install chromium
```

**Q: Out of memory**
- Upgrade Zeabur plan
- Optimize scraper memory usage

**Q: Build timeout**
- Increase build timeout in Zeabur settings
- Optimize build process

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

### Zeabur Monitoring
- Use Zeabur built-in monitoring
- Configure error alerts
- View application logs

### Vercel Analytics
- Enable Web Analytics
- Monitor performance metrics
- View access statistics

## 🔄 CI/CD Pipeline

### Automatic Deployment

1. **Code Push** → GitHub
2. **Zeabur Auto-build** → Backend deployment
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
   - [Zeabur Docs](https://docs.zeabur.com)
   - [Vercel Docs](https://vercel.com/docs)

---

🎉 Deployment complete! Your FollowNet application is now accessible globally. 