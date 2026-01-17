# ✅ Render Deployment Checklist

Use this checklist to ensure smooth deployment.

## Pre-Deployment

- [ ] Code is working locally (`python main.py`)
- [ ] All tests pass (if you have tests)
- [ ] `.env` file has all required variables
- [ ] `requirements.txt` is up to date
- [ ] You have your API keys ready:
  - [ ] Groq API key
  - [ ] OpenAI API key (for embeddings)

## GitHub Setup

- [ ] Code pushed to GitHub
- [ ] Repository is accessible
- [ ] Main branch is up to date
- [ ] `.env` is in `.gitignore` (don't commit secrets!)

## Render Configuration

- [ ] Signed up for Render account
- [ ] Connected GitHub account to Render
- [ ] Selected correct repository
- [ ] `render.yaml` detected automatically

## Environment Variables (Critical!)

Add these in Render Dashboard → Environment:

**Required Secrets:**
- [ ] `GROQ_API_KEY` = your_actual_groq_key
- [ ] `OPENAI_API_KEY` = your_actual_openai_key

**Update After Deployment:**
- [ ] `CORS_ORIGINS` = https://your-app-name.onrender.com

## Disk Storage

- [ ] Persistent disk added
- [ ] Mount path: `/opt/render/project/src/data`
- [ ] Size: At least 1GB

## Deployment

- [ ] Click "Manual Deploy" or "Apply Blueprint"
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Check logs for errors
- [ ] Build status shows "Live"

## Post-Deployment Testing

- [ ] Health check works: `https://your-app.onrender.com/health`
- [ ] API docs accessible: `https://your-app.onrender.com/docs`
- [ ] Can access homepage: `https://your-app.onrender.com/`
- [ ] Upload a test PDF
- [ ] Start an interview session
- [ ] Submit answers and get evaluations

## Production Readiness

- [ ] CORS origins updated with actual URL
- [ ] Logs are being generated
- [ ] Disk storage is working
- [ ] API keys are working
- [ ] Consider upgrading from free tier
- [ ] Set up monitoring/alerts
- [ ] Add authentication (if needed)
- [ ] Configure custom domain (optional)

## Troubleshooting

If something doesn't work:

1. **Check Render Logs**
   - Dashboard → Your Service → Logs
   - Look for error messages

2. **Verify Environment Variables**
   - Dashboard → Environment
   - Ensure all secrets are set

3. **Check Disk Mount**
   - Dashboard → Disks
   - Verify mount path is correct

4. **Test Locally First**
   - If it doesn't work locally, it won't work on Render
   - Fix local issues first

5. **Common Issues**
   - Missing API keys → Add in Environment
   - CORS errors → Update CORS_ORIGINS
   - File upload fails → Check disk mount
   - Slow first request → Free tier spin-down (normal)

## Support Resources

- [ ] Render Docs: https://render.com/docs
- [ ] Render Community: https://community.render.com
- [ ] Your deployment logs
- [ ] `DEPLOYMENT.md` for detailed guide

## Success Criteria

✅ Your deployment is successful when:
- Health endpoint returns `{"status":"healthy"}`
- You can upload a PDF
- Questions are generated
- Answers are evaluated
- No errors in logs

---

**Estimated Time:** 10-15 minutes total
**Cost:** Free tier available, $7/month for production
