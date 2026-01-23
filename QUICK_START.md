# 🚀 Quick Start Guide - Watsons Turkey Dashboard

## In 3 Steps

### 1️⃣ Ensure Data Files Are Ready
Make sure these files exist on your Desktop:
- `~/Desktop/baseline.csv`
- `~/Desktop/plan.csv`

### 2️⃣ Run the Dashboard
Open Terminal and run:
```bash
cd /Users/matteobrancato/Projects/watsons
./run_dashboard.sh
```

### 3️⃣ View the Dashboard
The dashboard will automatically open in your browser at:
**http://localhost:8501**

**Safari users**: If you see an HTTPS error, use this URL instead:
**http://127.0.0.1:8501**

---

## What You'll See

### Main Metrics (Top Row)
- ✅ **Automated**: Total automated tests
- 📋 **Backlog**: Tests waiting to be automated
- 🚫 **Blocked**: Tests currently blocked
- ➖ **Not Applicable**: Tests that can't be automated

### Summary Section (Bottom)
- Coverage breakdown with percentages
- Automation coverage rate
- Backlog-to-automated ratio

---

## Updating Data

1. Replace CSV files on Desktop (keep same names)
2. In browser, press `R` to refresh
3. Dashboard automatically loads new data

---

## Stopping the Dashboard

Press `Ctrl+C` in the Terminal

---

## Need Help?

See full documentation: [README.md](README.md)

Run tests: `python3 test_dashboard.py`
