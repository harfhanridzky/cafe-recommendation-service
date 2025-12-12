"""
Vercel serverless function entry point.
This file is required for Vercel deployment.
Uses Mangum to wrap FastAPI for serverless compatibility.
"""
from mangum import Mangum
from app.main import app

# Wrap FastAPI app with Mangum for Vercel serverless compatibility
handler = Mangum(app, lifespan="off")
