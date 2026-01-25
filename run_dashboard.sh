#!/bin/bash
# Watsons Turkey Automation Dashboard Launcher

set -e

echo "🚀 Watsons Turkey Automation Dashboard"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check/install dependencies
if ! python3 -c "import streamlit, pandas" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    python3 -m pip install -q -r requirements.txt
fi

# Run tests if data files exist
BASELINE="$HOME/Desktop/baseline.csv"
PLAN="$HOME/Desktop/plan.csv"

if [ -f "$BASELINE" ] && [ -f "$PLAN" ]; then
    echo "✅ Data files found - running tests..."
    if python3 test_processor.py > /dev/null 2>&1; then
        echo "✅ Tests passed"
    else
        echo "⚠️  Tests failed (run 'python3 test_processor.py' for details)"
    fi
else
    echo "ℹ️  Data files not on Desktop - upload via web interface"
fi

echo ""
echo "📊 Starting dashboard at http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

streamlit run dashboard.py
