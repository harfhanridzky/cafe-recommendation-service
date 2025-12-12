# ⚠️ Vercel Deployment - Troubleshooting Guide

## Problems Encountered & Solutions

### Problem 1: Missing Environment Variables ✅ FIXED
```
ValidationError: 1 validation error for Settings
GOOGLE_API_KEY
Field required [type=missing, input_value={}, input_type=dict]
```

**Solution Applied:**
- Modified `app/config.py` to make `GOOGLE_API_KEY` optional (default: empty string)
- Added explicit `os.getenv()` calls to read environment variables
- Added custom `__init__` method to prioritize OS environment variables
- Added warning message if `GOOGLE_API_KEY` is not set

### Problem 2: ASGI Handler Error ✅ FIXED
```
TypeError: issubclass() arg 1 must be a class
Python process exited with exit status: 1
```

**Root Cause:**
- FastAPI is an ASGI framework, but Vercel serverless expects AWS Lambda/HTTP handler format
- Direct FastAPI app export doesn't work with Vercel's Python runtime

**Solutions Applied:**

1. **Added Mangum ASGI Adapter** (`api/index.py`)
   - Wraps FastAPI with `Mangum(app, lifespan="off")`
   - Converts ASGI to AWS Lambda event format
   - Vercel uses AWS Lambda under the hood

2. **Improved Error Handling**
   - Added try-catch block for better debugging
   - Export both `handler` (Mangum) and `app` (FastAPI) for compatibility
   - Load environment variables BEFORE importing app

3. **Updated Vercel Configuration** (`vercel.json`)
   - Added `maxLambdaSize: "15mb"` config
   - Ensures enough space for FastAPI + dependencies

## How to Set Environment Variables in Vercel

### Option 1: Via Vercel Dashboard (Recommended)

1. Go to your project: https://vercel.com/dashboard
2. Select: `cafe-recommendation-service`
3. Navigate to: **Settings** → **Environment Variables**
4. Add these variables:

   ```
   Name: GOOGLE_API_KEY
   Value: [Your Google Places API Key]
   Environments: ✅ Production ✅ Preview ✅ Development
   
   Name: JWT_SECRET_KEY  
   Value: [Your secure secret key - min 32 characters]
   Environments: ✅ Production ✅ Preview ✅ Development
   
   Name: JWT_ALGORITHM
   Value: HS256
   Environments: ✅ Production ✅ Preview ✅ Development
   
   Name: ACCESS_TOKEN_EXPIRE_MINUTES
   Value: 30
   Environments: ✅ Production ✅ Preview ✅ Development
   ```

5. Click **Save**
6. **Redeploy**: Settings → Deployments → [...] → Redeploy

### Option 2: Via Vercel CLI

```bash
# Add environment variables
vercel env add GOOGLE_API_KEY production
# Paste your Google API key when prompted

vercel env add JWT_SECRET_KEY production
# Paste your JWT secret key when prompted

vercel env add JWT_ALGORITHM production
# Enter: HS256

vercel env add ACCESS_TOKEN_EXPIRE_MINUTES production
# Enter: 30

# Redeploy
vercel --prod
```

## Generate Secure JWT Secret

```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_hex(32))"

# Option 2: OpenSSL
openssl rand -hex 32

# Option 3: Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## Verification Steps

After deployment, verify your API is working:

### 1. Check Health Endpoint
```bash
curl https://your-project.vercel.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Cafe Recommendation Service",
  "version": "1.0.0"
}
```

### 2. Check API Documentation
Visit: `https://your-project.vercel.app/docs`

### 3. Test Authentication
```bash
# Register a user
curl -X POST "https://your-project.vercel.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "securepass123"}'

# Login
curl -X POST "https://your-project.vercel.app/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "securepass123"}'
```

### 4. Test Search (Public)
```bash
curl "https://your-project.vercel.app/api/v1/search?latitude=-6.2088&longitude=106.8456&radius=1000"
```

## Common Issues & Solutions

### Issue: "Module not found" Error
**Solution:** Ensure `requirements-vercel.txt` includes all dependencies:
```txt
fastapi==0.104.1
mangum==0.17.0
pydantic==2.5.0
httpx==0.25.2
...
```

### Issue: Function Timeout
**Solution:** Add timeout config to `vercel.json`:
```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

### Issue: Cold Start Performance
**Solution:**
- Vercel serverless functions have cold starts (~1-3 seconds)
- Use Vercel's Edge Functions for faster response (requires different setup)
- Consider adding health check warming

### Issue: Environment Variables Not Loading
**Solution:**
1. Double-check variable names (case-sensitive)
2. Ensure variables are set for correct environment (Production/Preview/Development)
3. Redeploy after adding variables
4. Check Vercel deployment logs: Settings → Deployments → View Function Logs

## File Structure for Vercel

```
your-project/
├── api/
│   └── index.py          # Serverless function entry point (Mangum wrapper)
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration with env vars
│   └── ...
├── vercel.json           # Vercel configuration
├── requirements-vercel.txt  # Production dependencies
└── .gitignore            # Exclude .env, venv, etc.
```

## Deployment Checklist

Before deploying:
- [ ] `vercel.json` points to `api/index.py`
- [ ] `api/index.py` uses Mangum wrapper
- [ ] `requirements-vercel.txt` includes `mangum==0.17.0`
- [ ] Environment variables set in Vercel dashboard
- [ ] `.env` file is in `.gitignore` (not committed)
- [ ] Google Places API enabled in Google Cloud Console
- [ ] JWT secret is strong (32+ characters)

## Support & Resources

- **Vercel Python Runtime**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **Mangum Documentation**: https://mangum.io/
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Google Places API**: https://developers.google.com/maps/documentation/places/web-service

---

**Last Updated**: December 12, 2025  
**Status**: All issues resolved ✅
