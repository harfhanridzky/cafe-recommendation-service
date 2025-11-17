#!/bin/bash

# Security Check Script - Run before git push
echo "🔒 Running Security Checks..."
echo ""

# Check 1: Is .env in gitignore?
echo "Check 1: Verifying .env is in .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo "✅ .env is in .gitignore"
else
    echo "❌ WARNING: .env is NOT in .gitignore!"
    echo "   Add it now: echo '.env' >> .gitignore"
    exit 1
fi
echo ""

# Check 2: Is .env tracked by git?
echo "Check 2: Verifying .env is not tracked..."
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ DANGER: .env is tracked by git!"
    echo "   Remove it: git rm --cached .env"
    exit 1
else
    echo "✅ .env is not tracked by git"
fi
echo ""

# Check 3: Check if .env exists and has API key
echo "Check 3: Verifying .env exists with API key..."
if [ -f .env ]; then
    if grep -q "GOOGLE_API_KEY=" .env && ! grep -q "your_google_places_api_key_here" .env; then
        echo "✅ .env exists with API key configured"
    else
        echo "⚠️  WARNING: .env exists but API key may not be configured"
    fi
else
    echo "⚠️  WARNING: .env file not found"
    echo "   Copy from template: cp .env.example .env"
fi
echo ""

# Check 4: Verify .env.example doesn't have real key
echo "Check 4: Verifying .env.example is safe..."
if [ -f .env.example ]; then
    if grep -q "your_google_places_api_key_here" .env.example || grep -q "YOUR_API_KEY" .env.example; then
        echo "✅ .env.example is safe (no real API key)"
    else
        echo "⚠️  WARNING: .env.example might contain a real API key!"
        echo "   Replace with placeholder"
    fi
else
    echo "⚠️  .env.example not found"
fi
echo ""

# Check 5: Look for potential API keys in staged files
echo "Check 5: Scanning staged files for potential secrets..."
if git diff --cached --name-only | xargs grep -l "AIza" 2>/dev/null; then
    echo "❌ DANGER: Found potential Google API key in staged files!"
    echo "   Review and remove before committing"
    exit 1
else
    echo "✅ No API keys found in staged files"
fi
echo ""

# Check 6: Verify pycache is ignored
echo "Check 6: Verifying __pycache__ is ignored..."
if grep -q "__pycache__" .gitignore; then
    echo "✅ __pycache__ is in .gitignore"
else
    echo "⚠️  WARNING: __pycache__ should be in .gitignore"
fi
echo ""

# Summary
echo "================================================"
echo "✅ Security checks completed!"
echo ""
echo "Safe to push if all checks passed ✅"
echo ""
echo "Before pushing:"
echo "  git add ."
echo "  git commit -m 'Your commit message'"
echo "  git push"
echo "================================================"
