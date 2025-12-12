# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add Vercel deployment config"
   git push origin main
   ```

2. **Import to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository: `harfhanridzky/cafe-recommendation-service`
   - Vercel will auto-detect the configuration

3. **Add Environment Variables** in Vercel Dashboard:
   - Go to Project Settings → Environment Variables
   - Add the following:
     ```
     GOOGLE_API_KEY=your_actual_google_places_api_key
     JWT_SECRET_KEY=your_secure_jwt_secret_key_min_32_chars
     JWT_ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     ```

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete
   - Your API will be live at: `https://your-project.vercel.app`

---

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N** (first time)
   - Project name? **cafe-recommendation-service**
   - Directory? **./** (current directory)

4. **Add Environment Variables**:
   ```bash
   vercel env add GOOGLE_API_KEY
   vercel env add JWT_SECRET_KEY
   vercel env add JWT_ALGORITHM
   vercel env add ACCESS_TOKEN_EXPIRE_MINUTES
   ```

5. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

---

## 📋 Deployment Checklist

Before deploying, ensure:

- [x] `vercel.json` configuration file created
- [x] `api/index.py` entry point created
- [x] `requirements-vercel.txt` created
- [ ] Environment variables configured in Vercel dashboard
- [ ] Code pushed to GitHub repository
- [ ] Google API Key is valid and has Places API enabled
- [ ] JWT Secret Key is strong (32+ characters)

---

## 🔧 Configuration Files Explanation

### 1. `vercel.json`
Configures how Vercel builds and routes your application:
- **builds**: Specifies Python runtime for FastAPI
- **routes**: Routes all requests to your FastAPI app
- **env**: Environment variables (secrets managed in Vercel dashboard)

### 2. `api/index.py`
Entry point for Vercel serverless functions:
- Exports your FastAPI app as `handler`
- Vercel automatically wraps it in ASGI server

### 3. `requirements-vercel.txt`
Production dependencies for Vercel deployment:
- Excludes testing dependencies (pytest, coverage, etc.)
- Includes `mangum` for ASGI/AWS Lambda compatibility

---

## 🌐 After Deployment

Your API will be available at:
```
https://your-project-name.vercel.app
```

### API Endpoints:

- **Documentation**: `https://your-project.vercel.app/docs`
- **Health Check**: `https://your-project.vercel.app/health`
- **Register**: `https://your-project.vercel.app/api/v1/auth/register`
- **Login**: `https://your-project.vercel.app/api/v1/auth/login`
- **Search**: `https://your-project.vercel.app/api/v1/search`
- **Recommendations**: `https://your-project.vercel.app/api/v1/recommendations`

---

## 🧪 Testing Your Deployment

```bash
# Set your Vercel URL
VERCEL_URL="https://your-project.vercel.app"

# 1. Health check
curl $VERCEL_URL/health

# 2. Register user
curl -X POST "$VERCEL_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# 3. Login
TOKEN=$(curl -s -X POST "$VERCEL_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | jq -r '.access_token')

# 4. Test search
curl "$VERCEL_URL/api/v1/search?lat=-6.2088&lng=106.8456&radius=1000"

# 5. Test recommendations (with auth)
curl "$VERCEL_URL/api/v1/recommendations?lat=-6.2088&lng=106.8456&min_rating=4.0" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔐 Managing Secrets in Vercel

### Via Dashboard:
1. Go to your project in Vercel
2. Settings → Environment Variables
3. Add each variable:
   - Name: `GOOGLE_API_KEY`
   - Value: Your actual key
   - Environments: Production, Preview, Development

### Via CLI:
```bash
# Production environment
vercel env add GOOGLE_API_KEY production

# All environments
vercel env add JWT_SECRET_KEY
```

### Generate Strong JWT Secret:
```bash
# macOS/Linux
openssl rand -hex 32

# Or Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚨 Troubleshooting

### Issue: Build fails with "Module not found"
**Solution**: Check `requirements-vercel.txt` includes all dependencies

### Issue: API returns 500 errors
**Solution**: Check environment variables are set correctly in Vercel dashboard

### Issue: "Function execution timeout"
**Solution**: Vercel free tier has 10s timeout. Optimize Google API calls or upgrade plan.

### Issue: CORS errors
**Solution**: Update CORS settings in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Vercel Deployment Limits

### Free Tier:
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Unlimited deployments
- ⚠️ 10s function timeout
- ⚠️ 50 MB function size

### Pro Tier ($20/month):
- ✅ 1 TB bandwidth
- ✅ 60s function timeout
- ✅ 50 MB function size
- ✅ Custom domains
- ✅ Team collaboration

---

## 🔄 Auto-Deploy from GitHub

Once connected to Vercel:

1. **Every push to `main`** → Auto-deploy to production
2. **Pull requests** → Preview deployments
3. **Branch pushes** → Automatic preview URLs

Configure in Vercel:
- Settings → Git → Production Branch: `main`
- Settings → Git → Auto-deploy: Enabled

---

## 📈 Monitoring

### View Logs:
```bash
vercel logs [deployment-url]
```

### View in Dashboard:
- Go to Deployments tab
- Click on deployment
- View real-time logs and function invocations

---

## 🎯 Custom Domain

1. Go to Project Settings → Domains
2. Add your custom domain: `api.yourdomain.com`
3. Configure DNS records as instructed by Vercel
4. Wait for SSL certificate provisioning (automatic)

---

## 💡 Best Practices

1. **Use Production Branch**: Keep `main` branch stable
2. **Test in Preview**: Use preview deployments for testing
3. **Monitor Usage**: Check function invocations in dashboard
4. **Secure Secrets**: Never commit `.env` or secrets to git
5. **Update Dependencies**: Keep `requirements-vercel.txt` updated
6. **Enable Analytics**: Vercel Analytics for performance monitoring

---

## 📞 Support

- **Vercel Docs**: https://vercel.com/docs
- **Vercel Support**: https://vercel.com/support
- **GitHub Issues**: https://github.com/harfhanridzky/cafe-recommendation-service/issues

---

## ✅ Success!

After deployment, your Cafe Recommendation Service API will be:
- 🌍 Globally distributed via Vercel Edge Network
- 🔒 Automatically secured with HTTPS
- 📊 Monitored with built-in analytics
- 🚀 Auto-deployed on every GitHub push
- ⚡ Serverless and auto-scaling

**Live URL**: `https://your-project.vercel.app/docs`
