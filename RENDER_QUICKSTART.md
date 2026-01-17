# 🚀 Render Deployment - Quick Start

## 5-Minute Deployment Guide

### Step 1: Push to GitHub (2 minutes)

```bash
# If not already a git repo
git init
git add .
git commit -m "Initial commit for Render deployment"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render (3 minutes)

1. **Go to Render**: https://dashboard.render.com/
2. **Click**: "New +" → "Blueprint"
3. **Connect**: Your GitHub repository
4. **Render detects** `render.yaml` automatically
5. **Add Secrets** (IMPORTANT!):
   - Click on the service name
   - Go to "Environment" tab
   - Add these as **Secret Files**:
     - `GROQ_API_KEY` = your_groq_api_key
     - `OPENAI_API_KEY` = your_openai_api_key
6. **Click**: "Apply" or "Create Web Service"

### Step 3: Wait for Deployment (5-10 minutes)

Watch the logs as Render:
- ✅ Installs dependencies
- ✅ Creates disk storage
- ✅ Starts your app

### Step 4: Test Your App

Your app will be at: `https://YOUR-APP-NAME.onrender.com`

Test it:
```bash
# Health check
curl https://YOUR-APP-NAME.onrender.com/health

# API docs
open https://YOUR-APP-NAME.onrender.com/docs
```

### Step 5: Update CORS (Important!)

1. Go to Environment tab
2. Find `CORS_ORIGINS`
3. Update to: `https://YOUR-APP-NAME.onrender.com`
4. Save (triggers redeploy)

## ✅ You're Live!

Your AI Viva Examiner is now deployed and accessible worldwide!

## 📝 Important Notes

**Free Tier Limitations:**
- App sleeps after 15 min of inactivity
- First request after sleep takes 30-60 seconds
- 750 hours/month free (enough for testing)

**For Production:**
- Upgrade to Starter plan ($7/month) for always-on
- Add more disk space if needed
- Consider PostgreSQL instead of SQLite

## 🔧 Troubleshooting

**Build fails?**
- Check logs in Render dashboard
- Verify requirements.txt is correct
- Ensure Python 3.11 compatibility

**App crashes?**
- Check environment variables are set
- Verify API keys are correct
- Check runtime logs

**Can't upload files?**
- Verify disk is mounted
- Check disk space
- Ensure MAX_FILE_SIZE_MB is set

## 📚 Full Documentation

See `DEPLOYMENT.md` for complete details.

## 🎉 Next Steps

1. Upload a test PDF
2. Run an interview session
3. Monitor logs and performance
4. Add authentication if needed
5. Set up custom domain (optional)

---

**Need help?** Check the logs in Render Dashboard → Your Service → Logs
