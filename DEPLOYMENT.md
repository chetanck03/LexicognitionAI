# Render Deployment Guide

## Prerequisites
- GitHub account
- Render account (sign up at https://render.com)
- Your Groq API key (and optionally OpenAI API key)

## Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Prepare for Render deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render

#### Option A: Using render.yaml (Recommended)

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click "Apply"

#### Option B: Manual Setup

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: ai-viva-examiner
   - **Region**: Oregon (US West) or closest to you
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Plan**: Free (or paid for better performance)

### 3. Add Environment Variables

In Render Dashboard → Your Service → Environment:

**Required (Add as Secret):**
- `GROQ_API_KEY` = your_groq_api_key_here
- `OPENAI_API_KEY` = your_openai_api_key (for embeddings)

**Important:**
- `CORS_ORIGINS` = https://your-app-name.onrender.com (update with your actual URL)

**Optional (already set in render.yaml):**
- `LLM_PROVIDER` = groq
- `LLM_MODEL` = llama-3.1-70b-versatile
- `PORT` = 10000 (Render sets this automatically)
- `HOST` = 0.0.0.0

### 4. Add Persistent Disk (Important!)

Your app needs storage for uploaded PDFs and vector stores:

1. In Render Dashboard → Your Service → "Disks"
2. Click "Add Disk"
3. Configure:
   - **Name**: data
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: 1 GB (free tier) or more
4. Save

### 5. Deploy

1. Click "Manual Deploy" → "Deploy latest commit"
2. Wait 5-10 minutes for build and deployment
3. Check logs for any errors

### 6. Access Your Application

Your app will be available at:
```
https://your-app-name.onrender.com
```

Test the health endpoint:
```
https://your-app-name.onrender.com/health
```

API documentation:
```
https://your-app-name.onrender.com/docs
```

## Post-Deployment

### Update CORS Origins

After deployment, update the CORS_ORIGINS environment variable:

1. Go to Environment tab
2. Update `CORS_ORIGINS` to include your actual Render URL:
   ```
   https://your-app-name.onrender.com
   ```
3. Save changes (this will trigger a redeploy)

### Monitor Your App

- **Logs**: Dashboard → Your Service → Logs
- **Metrics**: Dashboard → Your Service → Metrics
- **Health**: Check `/health` endpoint regularly

### Troubleshooting

**Build Fails:**
- Check Python version compatibility
- Verify all dependencies in requirements.txt
- Check build logs for specific errors

**App Crashes:**
- Check runtime logs
- Verify environment variables are set
- Ensure disk is mounted correctly

**Slow Performance (Free Tier):**
- Free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Upgrade to paid plan for always-on service

**File Upload Issues:**
- Verify disk is mounted at correct path
- Check disk space usage
- Ensure MAX_FILE_SIZE_MB is appropriate

## Upgrading from Free Tier

For production use, consider:

1. **Starter Plan ($7/month)**:
   - Always on (no spin-down)
   - Better performance
   - More disk space

2. **Add PostgreSQL** (instead of SQLite):
   - Better for concurrent users
   - More reliable
   - Render offers free PostgreSQL

3. **Add Redis** (for caching):
   - Faster response times
   - Session management
   - Render offers free Redis

## Automatic Deployments

Render automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render will automatically deploy
```

## Custom Domain (Optional)

1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records as instructed
4. Update CORS_ORIGINS to include your custom domain

## Security Checklist

- ✅ API keys stored as secrets (not in code)
- ✅ CORS configured for your domain only
- ✅ HTTPS enabled (automatic on Render)
- ✅ File upload size limits set
- ✅ Rate limiting (consider adding)
- ✅ Authentication (consider adding for production)

## Cost Estimate

**Free Tier:**
- Web Service: Free (with limitations)
- Disk: 1GB free
- Total: $0/month

**Production Setup:**
- Web Service (Starter): $7/month
- Disk (10GB): $1/month
- PostgreSQL: Free or $7/month
- Total: ~$8-15/month

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Your app logs: Dashboard → Logs

## Next Steps

1. Test all endpoints
2. Upload a sample PDF
3. Run a complete interview session
4. Monitor performance and logs
5. Consider adding authentication
6. Set up monitoring/alerts
