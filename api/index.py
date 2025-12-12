"""
Vercel serverless function entry point.
This file is required for Vercel deployment.
Uses Mangum to wrap FastAPI for AWS Lambda/Vercel serverless compatibility.
"""
import os
import sys

# Ensure environment variables are loaded BEFORE importing app
os.environ.setdefault("GOOGLE_API_KEY", "")
os.environ.setdefault("JWT_SECRET_KEY", "fallback_secret_key_please_set_in_vercel")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

# Import FastAPI app and Mangum
try:
    from mangum import Mangum
    from app.main import app as fastapi_app
    
    # Wrap FastAPI app with Mangum for Vercel serverless compatibility
    # Mangum converts ASGI (FastAPI) to AWS Lambda event format
    handler = Mangum(fastapi_app, lifespan="off")
    
    # Export app for direct ASGI usage (Vercel might look for this)
    app = fastapi_app
    
except Exception as e:
    print(f"Error initializing handler: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    raise
