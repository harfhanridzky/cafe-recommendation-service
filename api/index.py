"""
Vercel serverless function entry point.
This file is required for Vercel deployment.
Uses Mangum to wrap FastAPI for AWS Lambda/Vercel serverless compatibility.
"""
import os
from mangum import Mangum
from app.main import app

# Ensure environment variables are loaded
os.environ.setdefault("GOOGLE_API_KEY", "")
os.environ.setdefault("JWT_SECRET_KEY", "fallback_secret_key_please_set_in_vercel")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

# Wrap FastAPI app with Mangum for Vercel serverless compatibility
# Mangum converts ASGI (FastAPI) to AWS Lambda event format
handler = Mangum(app, lifespan="off")
