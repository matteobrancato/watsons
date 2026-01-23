#!/bin/bash

# Watsons Turkey Dashboard - Setup Verification Script
# Checks that everything is configured correctly before first run

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Watsons Turkey Dashboard - Setup Verification            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0

# Check Python
echo "🔍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "   ✅ Python found: $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check data files
echo "🔍 Checking data files..."
if [ -f "$HOME/Desktop/baseline.csv" ]; then
    SIZE=$(du -h "$HOME/Desktop/baseline.csv" | cut -f1)
    echo "   ✅ baseline.csv found ($SIZE)"
else
    echo "   ❌ baseline.csv not found at $HOME/Desktop/baseline.csv"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "$HOME/Desktop/plan.csv" ]; then
    SIZE=$(du -h "$HOME/Desktop/plan.csv" | cut -f1)
    echo "   ✅ plan.csv found ($SIZE)"
else
    echo "   ❌ plan.csv not found at $HOME/Desktop/plan.csv"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check project files
echo "🔍 Checking project files..."
FILES=("dashboard.py" "data_processor.py" "requirements.txt" "run_dashboard.sh")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file missing"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check dependencies
echo "🔍 Checking Python dependencies..."
if python3 -c "import streamlit" 2>/dev/null; then
    echo "   ✅ Streamlit installed"
else
    echo "   ⚠️  Streamlit not installed (will install on first run)"
fi

if python3 -c "import pandas" 2>/dev/null; then
    echo "   ✅ Pandas installed"
else
    echo "   ⚠️  Pandas not installed (will install on first run)"
fi
echo ""

# Check launcher permissions
echo "🔍 Checking launcher script..."
if [ -x "run_dashboard.sh" ]; then
    echo "   ✅ run_dashboard.sh is executable"
else
    echo "   ⚠️  Making run_dashboard.sh executable..."
    chmod +x run_dashboard.sh
    echo "   ✅ Fixed"
fi
echo ""

# Run integration test
echo "🔍 Running integration tests..."
if python3 test_dashboard.py > /dev/null 2>&1; then
    echo "   ✅ All tests passed"
else
    echo "   ❌ Tests failed (run 'python3 test_dashboard.py' for details)"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo "✅ VERIFICATION COMPLETE - All systems ready!"
    echo ""
    echo "You can now start the dashboard:"
    echo "   ./run_dashboard.sh"
else
    echo "❌ VERIFICATION FAILED - $ERRORS error(s) found"
    echo ""
    echo "Please fix the errors above before running the dashboard."
fi
echo "════════════════════════════════════════════════════════════"
