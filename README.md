# 📊 Watsons Turkey Automation Dashboard

Professional, clean, and intuitive dashboard for visualizing test automation metrics for Watsons Turkey BU.

## ✨ Features

- **Automated Tests**: Total count of automated test cases (UAT + Prod) with Desktop/Mobile breakdown
- **Smart Backlog**: Intelligent calculation of backlog items with deduplication logic for overlapping Desktop/Mobile tests
- **Blocked Tests**: Count of currently blocked test cases
- **Not Applicable Tests**: Smart breakdown by device type (Desktop/Mobile/Both)
- **Auto-refresh**: Simply replace CSV files with updated data (keeping the same filenames)
- **Coverage Metrics**: Automation coverage percentage and progress visualization
- **Clean UI**: Professional interface with progress bars and visual metrics

## 📁 Data Sources

The dashboard reads data from two CSV files on your Desktop:
- `~/Desktop/baseline.csv` - Baseline automation data
- `~/Desktop/plan.csv` - Automation plan data

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- macOS, Linux, or Windows

### Installation

1. Clone or navigate to the project directory:
```bash
cd /Users/matteobrancato/Projects/watsons
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Running the Dashboard

#### Option 1: Using the launcher script (Recommended)

```bash
./run_dashboard.sh
```

This script will:
- Check if dependencies are installed
- Verify data files exist
- Launch the dashboard automatically

#### Option 2: Using Streamlit directly

```bash
streamlit run dashboard.py
```

#### Option 3: Using Python directly

```bash
python3 -m streamlit run dashboard.py
```

The dashboard will automatically open in your default browser at `http://localhost:8501`

### Stopping the Dashboard

Press `Ctrl+C` in the terminal where the dashboard is running.

## 🧪 Testing

Run the integration tests to verify everything works correctly:

```bash
python3 test_dashboard.py
```

This will verify:
- Data files are accessible
- Data loads correctly
- All metrics calculate properly
- Data integrity is maintained

## 🧠 Smart Logic Explained

### Backlog Calculation (Smart Deduplication)

The dashboard intelligently handles overlapping test cases to avoid double-counting:

**Logic:**
- Tests with `Device = "Both"` that have the same status in Desktop and Mobile columns are counted **once** (not twice)
- Tests with `Device = "Desktop"` count only Desktop status
- Tests with `Device = "Mobile"` count only Mobile status
- This ensures accurate backlog metrics without inflation

**Example:**
```
ID: T123, Status Desktop: "Ready to be automated", Status Mobile: "Ready to be automated", Device: "Both"
→ Counted as: 1 backlog item (not 2)

ID: T456, Status Desktop: "Ready to be automated", Status Mobile: "Automated UAT", Device: "Both"
→ Counted as: 1 desktop backlog item
```

### Not Applicable Calculation (Smart Categorization)

Uses the `Device` column to properly categorize tests:
- `Desktop`: Tests not applicable for desktop only
- `Mobile`: Tests not applicable for mobile only
- `Both`: Tests not applicable for both platforms (counted once)

### Automated Tests

Counts from `baseline.csv` where status equals:
- "Automated UAT" or
- "Automated Prod"

Sums both Desktop and Mobile columns for total coverage.

### Blocked Tests

Counts from `plan.csv` where either Desktop or Mobile status = "Blocked".

## 🔄 Updating Data

To update the dashboard with new data:

1. **Replace the CSV files** on your Desktop with updated versions
2. **Keep the same filenames**: `baseline.csv` and `plan.csv`
3. **Refresh the dashboard** in your browser (press `R` or reload the page)

The dashboard will automatically detect and load the new data.

## 📂 Project Structure

```
watsons/
├── dashboard.py              # Main Streamlit dashboard application
├── data_processor.py         # Data processing and calculation logic
├── run_dashboard.sh          # Convenient launcher script
├── test_processor.py         # Basic processor test
├── test_dashboard.py         # Integration tests
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── .gitignore               # Git ignore file
```

## 📊 Metrics Breakdown

### ✅ Automated
**Source:** `baseline.csv`

**Calculation:**
- Desktop: Count where `Automation Status Testim Desktop` = "Automated UAT" or "Automated Prod"
- Mobile: Count where `Automation Status Testim Mobile View` = "Automated UAT" or "Automated Prod"
- Total: Sum of Desktop + Mobile

### 📋 Backlog (Smart)
**Source:** `plan.csv`

**Calculation:**
- Status matches: "In progress" OR "Ready to be automated"
- Smart deduplication based on `Device` column
- Breakdown: Desktop / Mobile / Both
- Total: Sum with no double-counting

### 🚫 Blocked
**Source:** `plan.csv`

**Calculation:**
- Count where status = "Blocked" in Desktop OR Mobile columns

### ➖ Not Applicable
**Source:** `plan.csv`

**Calculation:**
- Status: "Automation not applicable"
- Categorized by `Device` column (Desktop / Mobile / Both)
- Smart counting to avoid duplication

## 🔧 Technical Details

### Architecture
- **Clean separation of concerns**: Dashboard UI separate from data processing logic
- **Modular design**: Easy to maintain and extend
- **Type hints**: Better code readability and IDE support
- **Error handling**: Graceful handling of missing files or data issues

### Technologies
- **Streamlit**: Modern, reactive web framework for data dashboards
- **Pandas**: Efficient data manipulation and analysis
- **Python 3**: Clean, readable codebase

### Data Processing
- **Case-insensitive matching**: Handles variations in status text
- **Whitespace trimming**: Ensures data quality
- **Smart deduplication**: Prevents double-counting of shared tests
- **Efficient algorithms**: Fast processing even with large datasets

### UI/UX
- **Responsive layout**: Adapts to different screen sizes
- **Progress bars**: Visual representation of coverage
- **Color-coded metrics**: Easy to scan and understand
- **Clean typography**: Professional appearance

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check if Python is installed
python3 --version

# Install dependencies
pip install -r requirements.txt

# Try running directly
python3 -m streamlit run dashboard.py
```

### Data files not found
- Ensure `baseline.csv` and `plan.csv` are on your Desktop
- Check file paths: `~/Desktop/baseline.csv` and `~/Desktop/plan.csv`
- Verify files are not empty

### Dependencies error
```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Dashboard shows old data
- Refresh the browser (press `R`)
- Ensure you replaced the CSV files with the same filenames
- Clear browser cache if needed

### Safari shows "HTTPS-Only" error
Safari may block HTTP localhost connections. Solutions:
1. **Use IP address instead**: Open `http://127.0.0.1:8501` in Safari
2. **Disable HTTPS-Only for localhost**: Safari → Settings → Advanced → HTTPS-Only Mode
3. **Use another browser**: Chrome, Firefox, or Edge work perfectly
4. **See detailed guide**: [SAFARI_FIX.md](SAFARI_FIX.md)

## 📈 Current Metrics (Example)

Based on test run:
- **Automated:** 882 tests (Desktop: 472, Mobile: 410)
- **Backlog:** 564 tests (Smart count with deduplication)
- **Blocked:** 0 tests
- **Not Applicable:** 242 tests
- **Total Tests:** 1,688
- **Automation Coverage:** 61.0%

## 🤝 Contributing

To modify or extend the dashboard:

1. Edit `data_processor.py` for calculation logic changes
2. Edit `dashboard.py` for UI/layout changes
3. Run `test_dashboard.py` to verify changes
4. Update this README if adding new features

## 📝 License

Internal tool for Watsons Turkey BU.

## 👥 Support

For issues, questions, or feature requests, contact the development team.

---

**Built with ❤️ for Watsons Turkey**
