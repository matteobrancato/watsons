# 🦁 Safari HTTPS Issue - Solution

## The Problem
Safari might show this error when trying to open the dashboard:
> "Safari can't open the page http://localhost:8501/. The error is: Navigation failed because the request was for an HTTP URL with HTTPS-Only enabled"

## Quick Solution

### Option 1: Disable HTTPS-Only for Localhost (Recommended)

1. Open **Safari**
2. Go to **Safari** → **Settings** (or **Preferences**)
3. Click on **Advanced** tab
4. Find **"HTTPS-Only Mode"** or similar setting
5. Either:
   - **Uncheck** "HTTPS-Only Mode" completely, OR
   - Add `localhost` to exceptions

### Option 2: Use Another Browser

If you have Chrome, Firefox, or any other browser installed:

```bash
# The dashboard works perfectly in:
- Chrome
- Firefox
- Brave
- Edge
- Any Chromium-based browser
```

Simply open your browser and navigate to: **http://localhost:8501**

### Option 3: Manual URL Entry in Safari

1. Open Safari
2. In the address bar, type exactly: `http://localhost:8501`
3. Press Enter
4. If prompted about security, click **"Visit this website"** or **"Continue"**

## How to Check if It's Working

The dashboard is running if you see in Terminal:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

## Still Not Working?

Try restarting the dashboard:

```bash
# Stop the current dashboard (press Ctrl+C)
# Then restart:
./run_dashboard.sh
```

## Alternative Access Methods

### Use IP Address Instead of Localhost

Sometimes Safari accepts the IP address better:

```
http://127.0.0.1:8501
```

Try opening this URL in Safari instead of localhost.

## Why This Happens

Recent versions of Safari (14+) have HTTPS-Only mode enabled by default for security. Since the Streamlit dashboard runs locally on HTTP (not HTTPS), Safari blocks it.

This is normal and expected for local development tools. The dashboard is safe to access on localhost.

## Permanent Fix

If you use Safari frequently for development, add these to Safari exceptions:
- `localhost`
- `127.0.0.1`
- `0.0.0.0`

This allows you to access local development servers without security warnings.

---

**TL;DR**: Use **http://127.0.0.1:8501** in Safari or switch to Chrome/Firefox.
