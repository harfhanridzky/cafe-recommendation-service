"""
Vercel serverless function entry point.
This file is required for Vercel deployment.
"""
from app.main import app

# Vercel requires the app to be exported as 'app' or 'handler'
handler = app
