#!/bin/bash

# Watsons Turkey Automation Dashboard Launcher
# Simple script to start the dashboard

echo "🚀 Starting Watsons Turkey Automation Dashboard..."
echo ""

# Check if dependencies are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    python3 -m pip install -r requirements.txt
    echo ""
fi

# Check if data files exist
if [ ! -f "$HOME/Desktop/baseline.csv" ]; then
    echo "❌ Error: baseline.csv not found on Desktop"
    echo "   Please ensure the file exists at: $HOME/Desktop/baseline.csv"
    exit 1
fi

if [ ! -f "$HOME/Desktop/plan.csv" ]; then
    echo "❌ Error: plan.csv not found on Desktop"
    echo "   Please ensure the file exists at: $HOME/Desktop/plan.csv"
    exit 1
fi

echo "✅ Data files found"
echo "📊 Launching dashboard..."
echo ""

# Detect and use best browser
if command -v firefox &> /dev/null || [ -d "/Applications/Firefox.app" ]; then
    echo "   Opening in Firefox: http://localhost:8501"
elif command -v google-chrome &> /dev/null || [ -d "/Applications/Google Chrome.app" ]; then
    echo "   Opening in Chrome: http://localhost:8501"
else
    echo "   Dashboard URL: http://localhost:8501"
    echo "   If Safari shows HTTPS error, use: http://127.0.0.1:8501"
fi

echo "   Press Ctrl+C to stop the dashboard"
echo ""

# Run Streamlit with browser detection
export BROWSER=""
if [ -d "/Applications/Firefox.app" ]; then
    export BROWSER="open -a Firefox"
elif [ -d "/Applications/Google Chrome.app" ]; then
    export BROWSER="open -a 'Google Chrome'"
fi

streamlit run dashboard.py
