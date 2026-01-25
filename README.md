# Watsons Turkey Automation Dashboard

Streamlit dashboard for test automation metrics with smart deduplication.

## Quick Start

```bash
# Install & run
pip install -r requirements.txt
streamlit run dashboard.py

# Or use the launcher
./run_dashboard.sh
```

Open http://localhost:8501 and upload your CSV files.

## Metrics

| Metric | Description |
|--------|-------------|
| **Automated** | Tests with "Automated UAT" or "Automated Prod" status |
| **Backlog** | "In progress" or "Ready to be automated" (deduplicated) |
| **Blocked** | Currently blocked tests |
| **Not Applicable** | Tests not suitable for automation |

## CSV Format

**Baseline CSV** - Required columns:
- `Automation Status Testim Desktop`
- `Automation Status Testim Mobile View`

**Plan CSV** - Required columns:
- `Automation Status Testim Desktop`
- `Automation Status Testim Mobile View`
- `Device` (Desktop, Mobile, or Both)

## Smart Deduplication

Tests marked as "Both" (Desktop AND Mobile) are counted once, not twice:

```
Test: T123, Device: "Both"
Desktop Status: "Ready to be automated"
Mobile Status: "Ready to be automated"
→ Counted as 1 backlog item (not 2)
```

## Files

```
dashboard.py       # Main Streamlit application
data_processor.py  # Data processing logic
test_processor.py  # Test suite
run_dashboard.sh   # Launcher script
requirements.txt   # Dependencies
```

## Testing

```bash
python3 test_processor.py
```

Requires `baseline.csv` and `plan.csv` on Desktop.
