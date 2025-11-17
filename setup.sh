#!/bin/bash

# Cafe Recommendation Service - Setup Script

echo "🚀 Setting up Cafe Recommendation Service..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit .env and add your Google Places API key!"
    echo "   Get your API key: https://developers.google.com/maps/documentation/places/web-service/get-api-key"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GOOGLE_API_KEY"
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo "3. Run the server:"
echo "   uvicorn app.main:app --reload"
echo "4. Visit http://localhost:8000/docs"
echo ""
