# 📊 Watsons Turkey Automation Dashboard

Professional Streamlit dashboard for visualizing test automation metrics with smart deduplication logic.

## Features

- **File Upload**: Drag & drop CSV files directly in the browser
- **Smart Deduplication**: Intelligent handling of overlapping Desktop/Mobile test cases
- **Real-time Processing**: Instant metrics calculation upon file upload
- **Clean UI**: Professional design with clear, bold metrics
- **Responsive Layout**: Works on desktop and tablet devices

## Metrics Calculated

### ✅ Automated
Total automated test cases from baseline file:
- Desktop automated (UAT + Prod)
- Mobile automated (UAT + Prod)
- Combined total with breakdown

### 📋 Backlog (Smart)
Backlog items with intelligent deduplication:
- Tests marked "In progress" or "Ready to be automated"
- Smart counting prevents double-counting of "Both" device tests
- Breakdown: Desktop / Mobile / Both

### 🚫 Blocked
Count of currently blocked test cases from plan file

### ➖ Not Applicable
Tests not applicable for automation, categorized by device type:
- Desktop only
- Mobile only
- Both platforms

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard.py
```

Open `http://localhost:8501` in your browser.

### Streamlit Cloud Deployment

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy automatically

## File Format

### Baseline CSV
Required columns:
- `Automation Status Testim Desktop`
- `Automation Status Testim Mobile View`

Expected values: `Automated UAT`, `Automated Prod`

### Plan CSV
Required columns:
- `Automation Status Testim Desktop`
- `Automation Status Testim Mobile View`
- `Device` (Desktop, Mobile, or Both)

Expected values: `In progress`, `Ready to be automated`, `Blocked`, `Automation not applicable`

## Smart Deduplication Logic

The dashboard intelligently handles test cases that apply to both Desktop and Mobile:

**Example:**
```
Test ID: T123
Desktop Status: "Ready to be automated"
Mobile Status: "Ready to be automated"
Device: "Both"
→ Counted as: 1 backlog item (not 2)
```

**Logic:**
- If `Device = "Both"` and both statuses match → Count once
- If `Device = "Desktop"` → Count desktop only
- If `Device = "Mobile"` → Count mobile only
- Prevents inflation of metrics from duplicate counting

## Project Structure

```
watsons/
├── dashboard.py          # Main Streamlit application
├── data_processor.py     # Data processing and calculation logic
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Technical Stack

- **Streamlit** - Web framework for data dashboards
- **Pandas** - Data manipulation and analysis
- **Python 3.8+** - Core programming language

## Usage

1. **Launch dashboard** (locally or on Streamlit Cloud)
2. **Upload baseline CSV** in the first upload box
3. **Upload plan CSV** in the second upload box
4. **View metrics** automatically calculated and displayed

Files can have any name - only the content structure matters.

## Development

### Run Locally
```bash
streamlit run dashboard.py
```

### Test Data Processing
```bash
python3 test_dashboard.py
```

### Code Quality
- Clean, readable code with docstrings
- Type hints for better IDE support
- Modular architecture (UI separate from logic)
- Error handling for missing/malformed data

## License

Internal tool for Watsons Turkey BU.

## Support

For issues or questions, contact the development team.

---

**Built with attention to detail and professional standards**
