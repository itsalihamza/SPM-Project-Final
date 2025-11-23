# 🚀 Deployment to Render.com - Step by Step

## Step 1: Push to GitHub

```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ad Intelligence Agent"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ad-intelligence-agent.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Render

1. **Go to** https://render.com
2. **Sign up** with GitHub
3. Click **"New +"** → **"Web Service"**
4. **Connect your repository**: `ad-intelligence-agent`
5. **Configure**:
   - **Name**: `ad-intelligence-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

6. Click **"Create Web Service"**

## Step 3: Wait for Deployment

Render will:
- Clone your repo
- Install dependencies
- Start your server
- Give you a URL like: `https://ad-intelligence-agent.onrender.com`

**First deployment takes 5-10 minutes**

## Step 4: Test Your Deployed API

```powershell
# Health check
curl https://YOUR-APP.onrender.com/health

# Collect ads
curl -X POST https://YOUR-APP.onrender.com/api/v1/collect `
  -H "Content-Type: application/json" `
  -d '{\"keywords\": [\"Nike\"], \"platform\": \"mock\", \"max_results\": 5}'
```

## Step 5: View API Docs

Visit: `https://YOUR-APP.onrender.com/docs`

---

## ⚠️ Important Notes

### Free Tier Limitations
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free

### For Production
Upgrade to paid plan ($7/month) for:
- No spin-down
- Faster performance
- Custom domain

---

## 🐛 Troubleshooting

### Build fails
- Check `requirements.txt` is correct
- View build logs on Render dashboard

### Server won't start
- Check start command is correct
- View logs on Render dashboard

### API returns errors
- Check environment variables
- View application logs

---

## 📝 Your Deployed URLs

Once deployed, you'll have:
- **API**: `https://YOUR-APP.onrender.com`
- **Health**: `https://YOUR-APP.onrender.com/health`
- **Docs**: `https://YOUR-APP.onrender.com/docs`
- **Collect**: `https://YOUR-APP.onrender.com/api/v1/collect`

---

## ✅ Verification Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Build completed successfully
- [ ] Server is running
- [ ] Health check returns 200
- [ ] API docs accessible
- [ ] Can collect ads via API

---

## 🎉 You're Done!

Your Ad Intelligence Agent is now live and accessible from anywhere!
