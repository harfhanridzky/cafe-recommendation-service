# 🚀 Quick Deploy to Vercel - Visual Guide

```
┌─────────────────────────────────────────────────────────────┐
│           CAFE RECOMMENDATION SERVICE                        │
│           Deploy to Vercel in 3 Steps                       │
└─────────────────────────────────────────────────────────────┘

STEP 1: Push to GitHub
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your Computer                    GitHub
    📁 Project                     ☁️  Repository
       │                           │
       │  git add .               │
       │  git commit -m "msg"     │
       │  git push origin main    │
       └──────────────────────────▶
       

STEP 2: Import to Vercel
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    1. Go to vercel.com
       └─▶ Click "Add New Project"
    
    2. Import Repository
       └─▶ Select: harfhanridzky/cafe-recommendation-service
    
    3. Configure Project
       ├─▶ Framework Preset: Other
       ├─▶ Root Directory: ./
       └─▶ Build Command: (auto-detected)


STEP 3: Add Environment Variables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Project Settings → Environment Variables
    
    ┌───────────────────────────────────────────────────┐
    │  Variable Name              │  Value              │
    ├─────────────────────────────┼─────────────────────┤
    │  GOOGLE_API_KEY            │  AIza...            │
    │  JWT_SECRET_KEY            │  your_secret_key    │
    │  JWT_ALGORITHM             │  HS256              │
    │  ACCESS_TOKEN_EXPIRE_MIN   │  30                 │
    └───────────────────────────────────────────────────┘


✅ DEPLOYMENT COMPLETE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your API is now live at:
🌐 https://your-project.vercel.app

API Documentation:
📚 https://your-project.vercel.app/docs

Test your API:
🧪 https://your-project.vercel.app/health


AUTO-DEPLOYMENT ENABLED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every time you push to GitHub:

    git push origin main
         │
         ▼
    ┌─────────────┐
    │   GitHub    │  Triggers webhook
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   Vercel    │  Auto-builds & deploys
    └──────┬──────┘
           │
           ▼
    ✅ Live in ~30 seconds!


ARCHITECTURE ON VERCEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Internet Users
      │
      ▼
┌──────────────────────┐
│   Vercel Edge CDN    │  ← Global distribution
│   (150+ locations)   │  ← Auto HTTPS/SSL
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Serverless Function │  ← Your FastAPI app
│  (Auto-scaling)      │  ← 0-∞ instances
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Google Places API   │  ← External service
└──────────────────────┘


COST: FREE TIER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 100 GB bandwidth/month
✅ Unlimited deployments
✅ Automatic HTTPS
✅ Custom domains
✅ Preview deployments
⚠️  10s function timeout


VERCEL CLI ALTERNATIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Terminal Commands:

    # Install Vercel CLI
    $ npm install -g vercel
    
    # Login
    $ vercel login
    
    # Deploy (preview)
    $ vercel
    
    # Deploy (production)
    $ vercel --prod
    
    # View logs
    $ vercel logs
    
    # Add secrets
    $ vercel env add GOOGLE_API_KEY


TEST YOUR DEPLOYMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

URL="https://your-project.vercel.app"

# 1. Health check
curl $URL/health

# 2. Register
curl -X POST "$URL/api/v1/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{"email":"test@example.com","password":"test123"}'

# 3. Login
curl -X POST "$URL/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{"email":"test@example.com","password":"test123"}'

# 4. Search cafes
curl "$URL/api/v1/search?lat=-6.2088&lng=106.8456"


TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Build Failed
   → Check vercel.json syntax
   → Verify requirements-vercel.txt

❌ 500 Errors
   → Check environment variables in Vercel dashboard
   → View logs: vercel logs [deployment-url]

❌ Module Not Found
   → Ensure all dependencies in requirements-vercel.txt
   → Check Python version compatibility

❌ Timeout Errors
   → Free tier: 10s limit
   → Optimize API calls
   → Consider Pro plan ($20/mo, 60s timeout)


MONITORING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Vercel Dashboard → Your Project:

├── 📊 Analytics
│   ├── Request count
│   ├── Response times
│   └── Error rates
│
├── 🚀 Deployments
│   ├── Production
│   ├── Preview (PR)
│   └── Development
│
├── 📝 Logs
│   ├── Real-time
│   ├── Function invocations
│   └── Error traces
│
└── ⚙️  Settings
    ├── Environment Variables
    ├── Domains
    └── Git Integration


CUSTOM DOMAIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to: Project Settings → Domains
2. Add: api.yourdomain.com
3. Configure DNS:
   
   Type    Name    Value
   ────────────────────────────────────
   CNAME   api     cname.vercel-dns.com
   
4. Wait for SSL (automatic, ~5 minutes)
5. Done! → https://api.yourdomain.com


NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After successful deployment:

✅ Update README with your Vercel URL
✅ Test all endpoints
✅ Enable Vercel Analytics
✅ Setup monitoring alerts
✅ Add custom domain (optional)
✅ Share your API! 🎉


SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Full Guide: VERCEL_DEPLOYMENT.md
🐛 Issues: github.com/harfhanridzky/cafe-recommendation-service/issues
💬 Vercel Support: vercel.com/support
📖 Vercel Docs: vercel.com/docs

```
