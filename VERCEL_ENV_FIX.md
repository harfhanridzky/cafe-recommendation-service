# ⚠️ Vercel Deployment - Environment Variables Fix

## Problems Encountered

### Problem 1: Missing Environment Variables
```
ValidationError: 1 validation error for Settings
GOOGLE_API_KEY
Field required [type=missing, input_value={}, input_type=dict]
```

### Problem 2: ASGI Handler Error
```
TypeError: issubclass() arg 1 must be a class
Python process exited with exit status: 1
```

### Problem 2: ASGI Handler Error
```
TypeError: issubclass() arg 1 must be a class
Python process exited with exit status: 1
```

## Solutions Applied

### 1. Fixed `app/config.py` (Environment Variables Issue)
- Changed `GOOGLE_API_KEY` from required field to optional with default empty string
- Added explicit `os.getenv()` calls to read environment variables
- Added custom `__init__` method to prioritize OS environment variables (for Vercel)
- Added warning message if `GOOGLE_API_KEY` is not set

### 2. Fixed `vercel.json` (Build Configuration)
- Changed build source from `app/main.py` to `api/index.py`
- Removed `env` section (environment variables should be set in Vercel dashboard)
- Simplified routes configuration

### 3. Fixed `api/index.py` (ASGI Handler Issue) ⭐ NEW
- **Problem**: FastAPI is ASGI, but Vercel expected WSGI/HTTP handler
- **Solution**: Wrapped FastAPI app with `Mangum` ASGI adapter
- **Changed**: `handler = app` → `handler = Mangum(app, lifespan="off")`
- **Why**: Mangum converts ASGI (FastAPI) to AWS Lambda/Vercel compatible format

### 3. Fixed `api/index.py` (ASGI Handler Issue) ⭐ NEW
- **Problem**: FastAPI is ASGI, but Vercel expected WSGI/HTTP handler
- **Solution**: Wrapped FastAPI app with `Mangum` ASGI adapter
- **Changed**: `handler = app` → `handler = Mangum(app, lifespan="off")`
- **Why**: Mangum converts ASGI (FastAPI) to AWS Lambda/Vercel compatible format

## How to Set Environment Variables in Vercel

### Option 1: Via Vercel Dashboard (Recommended)

1. Go to your project in Vercel: https://vercel.com/dashboard
2. Click on your project: `cafe-recommendation-service`
3. Go to: **Settings** → **Environment Variables**
4. Add the following variables:

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
6. **Redeploy** your project (Settings → Deployments → [...] → Redeploy)

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
# Option 1: Using openssl (macOS/Linux)
openssl rand -hex 32

# Option 2: Using Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Option 3: Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## Verification Steps

After setting environment variables and redeploying:

1. **Check Deployment Logs**:
   - Go to Vercel Dashboard → Deployments
   - Click on latest deployment
   - View "Build Logs" and "Function Logs"
   - Should NOT see validation errors

2. **Test Health Endpoint**:
   ```bash
   curl https://your-project.vercel.app/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "Cafe Recommendation Service"
   }
   ```

3. **Test API Documentation**:
   Open: `https://your-project.vercel.app/docs`
   Should see Swagger UI

4. **Test Register Endpoint**:
   ```bash
   curl -X POST "https://your-project.vercel.app/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123456"}'
   ```

5. **Test Search Endpoint** (requires GOOGLE_API_KEY):
   ```bash
   curl "https://your-project.vercel.app/api/v1/search?lat=-6.2088&lng=106.8456&radius=1000"
   ```

## Common Issues & Solutions

### Issue: Still getting "Field required" error
**Solution**: 
- Ensure environment variables are saved in **all environments** (Production, Preview, Development)
- Redeploy after adding variables
- Check variable names match exactly (case-sensitive)

### Issue: API returns empty results
**Solution**:
- Verify `GOOGLE_API_KEY` is valid
- Check Google Places API is enabled in Google Cloud Console
- Check API key has no restrictions blocking Vercel's IP ranges

### Issue: JWT authentication fails
**Solution**:
- Verify `JWT_SECRET_KEY` is at least 32 characters
- Ensure `JWT_ALGORITHM` is set to `HS256`
- Check `ACCESS_TOKEN_EXPIRE_MINUTES` is a valid number

## Files Changed

- ✅ `app/config.py` - Made environment variables optional with defaults
- ✅ `vercel.json` - Fixed build configuration
- ✅ `app/config.py.backup` - Backup of original config

## Next Steps

1. **Set environment variables** in Vercel dashboard
2. **Redeploy** your application
3. **Test endpoints** to verify everything works
4. **Monitor logs** for any warnings or errors

## Support

If you continue to have issues:
1. Check Vercel function logs: `vercel logs [deployment-url]`
2. View deployment logs in Vercel dashboard
3. Test locally first: `vercel dev`
4. Open GitHub issue with error details

---

**Updated**: December 12, 2025
**Status**: ✅ Fixed - Ready to redeploy
