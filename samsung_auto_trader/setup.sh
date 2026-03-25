#!/bin/bash
# Setup script for Samsung Electronics Auto Trader

echo "🚀 Samsung Electronics Auto Trader Setup"
echo "================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $python_version"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check environment variables
echo ""
echo "🔐 Checking environment variables..."

if [ -z "$GH_APPKEY" ]; then
    echo "❌ GH_APPKEY not set"
    echo "   Please set: export GH_APPKEY='your_app_key'"
else
    echo "✅ GH_APPKEY set"
fi

if [ -z "$GH_APPSECRET" ]; then
    echo "❌ GH_APPSECRET not set"
    echo "   Please set: export GH_APPSECRET='your_app_secret'"
else
    echo "✅ GH_APPSECRET set"
fi

if [ -z "$GH_ACCOUNT" ]; then
    echo "❌ GH_ACCOUNT not set"
    echo "   Please set: export GH_ACCOUNT='12345678-01'"
else
    echo "✅ GH_ACCOUNT set: $GH_ACCOUNT"
fi

# Summary
echo ""
echo "================================================"
echo "✅ Setup complete!"
echo ""
echo "To run the trader:"
echo "  python main.py"
echo ""
echo "To test for 5 minutes:"
echo "  python main.py --test-duration 5"
echo ""
echo "For help:"
echo "  python main.py --help"
echo "================================================"
