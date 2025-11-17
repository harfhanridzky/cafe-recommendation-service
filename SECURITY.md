# 🔒 Security Guidelines

## API Key Protection

### ✅ What's Protected (Won't be pushed to GitHub):

1. **`.env` file** - Contains your actual API key
   - Already in `.gitignore`
   - Never commit this file!

2. **`__pycache__/`** - Python cache files
3. **`venv/`** - Virtual environment
4. **`.DS_Store`** - macOS system files

### ⚠️ What Will Be Pushed (Public):

1. **`.env.example`** - Template without real API key
   ```
   GOOGLE_API_KEY=your_google_places_api_key_here
   ```

2. **All source code** - Safe to share
3. **Documentation** - Safe to share

## Before First Push - Verification Checklist:

```bash
# 1. Check if .env is ignored
git status --ignored | grep .env

# 2. Check what files will be committed
git status

# 3. If you see .env in "to be committed" - STOP!
git reset .env

# 4. Ensure .gitignore has .env
cat .gitignore | grep "^\.env$"
```

## If You Accidentally Pushed API Key:

### ⚠️ CRITICAL STEPS:

1. **Immediately revoke the API key** at:
   https://console.cloud.google.com/apis/credentials

2. **Generate a new API key**

3. **Remove from Git history:**
   ```bash
   # Use BFG Repo-Cleaner or git filter-branch
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```

4. **Update local .env with new key**

## Best Practices:

### 1. Use Environment Variables (Already Implemented ✅)
```python
# config.py
GOOGLE_API_KEY: str  # Loaded from .env
```

### 2. Never Hardcode API Keys
❌ BAD:
```python
api_key = "AIzaSyBy7A9QrkSIMhG2E7fA66SC0MHu-XOmZv8"
```

✅ GOOD:
```python
api_key = os.getenv("GOOGLE_API_KEY")
```

### 3. Use Different Keys for Dev/Prod
- Development: Limited quota key
- Production: Production key with IP restrictions

### 4. Enable API Key Restrictions (Recommended):

Go to Google Cloud Console:
1. **Application restrictions**:
   - HTTP referrers (for web)
   - IP addresses (for server)
   
2. **API restrictions**:
   - Restrict to: Places API only

### 5. Monitor API Usage:
- Check for unusual activity
- Set up budget alerts
- Review logs regularly

## Testing Without Exposing Key:

### For Team Members:
```bash
# Each developer gets their own key
cp .env.example .env
# Edit .env with their personal API key
```

### For CI/CD:
```bash
# Use GitHub Secrets / GitLab CI Variables
# Never put in code or config files
```

## Additional Security Layers:

### 1. Rate Limiting (Can be added):
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("5/minute")
@app.get("/api/v1/search")
async def search_cafes(...):
    ...
```

### 2. API Authentication (Can be added):
```python
from fastapi.security import APIKeyHeader
api_key_header = APIKeyHeader(name="X-API-Key")

@app.get("/api/v1/search")
async def search_cafes(api_key: str = Depends(api_key_header)):
    if api_key != INTERNAL_API_KEY:
        raise HTTPException(403)
    ...
```

## Quick Security Check:

```bash
# Before pushing to GitHub
./security_check.sh
```

## Resources:

- [Google API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

---

**Remember**: Prevention is better than revocation! Always verify before `git push`.
