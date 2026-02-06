# Investment Portfolio Tracker

A comprehensive Python-based investment portfolio tracking system with automated daily emails, Google Calendar integration, and intelligent options recommendations. Built for personal use with n8n workflow automation.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [File Structure](#file-structure)
- [Configuration](#configuration)
- [Daily Automation Schedule](#daily-automation-schedule)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Extension Ideas](#extension-ideas)
- [Key Learnings and Best Practices](#key-learnings-and-best-practices)

---

## Project Overview

This project automates the daily tracking of a personal investment portfolio, providing:

- Real-time market data fetching via Yahoo Finance
- Portfolio valuation with daily P&L calculations
- Options position tracking with expiration monitoring
- Prioritized action recommendations for options management
- Dual daily email reports (morning preview & afternoon recap)
- Google Calendar integration for options expiration reminders
- HTTP API for integration with other tools

The system is designed to run autonomously via Windows Task Scheduler and n8n workflows, delivering actionable insights directly to your inbox.

---

## Key Features

### Portfolio Tracking
- Automatic loading from brokerage CSV exports
- Real-time stock price updates via yfinance
- Daily gain/loss calculations per position
- Total portfolio value and performance metrics

### Options Analysis
- Parses complex option symbols (e.g., "NVDA Feb 27 '26 $195 Call")
- Tracks days to expiration with countdown
- Calculates P&L for each options position
- Identifies short vs long positions

### Action Recommendations
- Priority scoring algorithm (time urgency + loss severity)
- Four urgency levels: CRITICAL, HIGH, MEDIUM, LOW
- Profit-taking opportunities for short positions at 50%+ gain
- Expiring this week/next week categorization

### Dual Daily Emails
- **Morning Preview (6:30 AM)**: Pre-market futures, VIX levels, today's expirations, key positions to watch
- **Afternoon Recap (1:00 PM)**: Market performance, portfolio vs S&P 500, top gainers/losers, options summary

### Calendar Integration
- Creates Google Calendar events for each option expiration
- Color-coded by P&L (green = profit, red = loss)
- Multiple reminders (30 days, 7 days, 1 day before)
- Auto-updates events with latest P&L data

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Investment Portfolio Tracker                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐  │
│  │  Brokerage CSV  │───▶│  load_portfolio  │───▶│ daily_market_summary│  │
│  │  (Portfolio.csv)│    │       .py        │    │         .py         │  │
│  └─────────────────┘    └──────────────────┘    └──────────┬──────────┘  │
│                                                             │             │
│                                                             ▼             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐  │
│  │  Yahoo Finance  │───▶│    yfinance      │───▶│    JSON Output      │  │
│  │      API        │    │    library       │    │  (stdout/HTTP)      │  │
│  └─────────────────┘    └──────────────────┘    └──────────┬──────────┘  │
│                                                             │             │
├─────────────────────────────────────────────────────────────┼─────────────┤
│                                                             │             │
│  ┌─────────────────┐                            ┌──────────▼──────────┐  │
│  │   serve.py      │◀───────HTTP API───────────▶│     n8n Workflow    │  │
│  │  (Port 8080)    │                            │                     │  │
│  └─────────────────┘                            └──────────┬──────────┘  │
│                                                             │             │
│  ┌─────────────────┐                            ┌──────────▼──────────┐  │
│  │ calendar_sync   │───▶ Google Calendar API ───▶│   Email (Gmail)     │  │
│  │      .py        │                            │                     │  │
│  └─────────────────┘                            └─────────────────────┘  │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                      Windows Task Scheduler                               │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  6:00 AM  │  calendar_sync.py --update-all                          │ │
│  │  6:30 AM  │  n8n triggers morning email workflow                    │ │
│  │  1:00 PM  │  n8n triggers afternoon email workflow                  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Interaction

1. **Portfolio Data**: Exported CSV from brokerage is placed in `private_data/`
2. **Market Data**: `daily_market_summary.py` fetches live prices via yfinance
3. **HTTP Server**: `serve.py` exposes JSON API on port 8080
4. **n8n Workflow**: Fetches data from HTTP API, formats HTML email, sends via Gmail
5. **Calendar Sync**: Task Scheduler runs `calendar_sync.py` daily to update events
6. **Google Calendar**: Displays options expirations with reminders

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Core runtime |
| n8n | Latest | Workflow automation |
| Git | Any | Version control |

### Required Accounts

| Service | Purpose |
|---------|---------|
| Google Cloud | Calendar API access |
| Gmail | SMTP for sending emails |
| Brokerage | CSV export of portfolio |

### Python Packages

```
yfinance
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```

---

## Installation

### Step 1: Clone or Create Project Directory

```bash
mkdir C:\scripts\investment-summary
cd C:\scripts\investment-summary
git init
```

### Step 2: Install Python Dependencies

```bash
pip install yfinance google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 3: Create Private Data Directory

```bash
mkdir private_data
```

This folder is git-ignored and stores sensitive data:
- `portfolio.csv` - Your brokerage export
- `google_credentials.json` - OAuth credentials from Google Cloud
- `token.json` - Auto-generated after first authentication

### Step 4: Set Up Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the **Google Calendar API**
4. Go to **Credentials** > **Create Credentials** > **OAuth client ID**
5. Select **Desktop application**
6. Download the JSON file
7. Save as `private_data/google_credentials.json`

### Step 5: First-Time Calendar Authentication

```bash
python calendar_sync.py --create-all --dry-run
```

This will open a browser for OAuth consent. After approval, `token.json` is created.

### Step 6: Export Portfolio from Brokerage

Export your portfolio as CSV and save to `private_data/portfolio.csv`.

Required columns:
- `Symbol` - Stock symbol or option description
- `Quantity` - Number of shares/contracts
- `Last Price $` - Current price
- `Day's Gain $` - Today's change
- `Total Gain $` - Overall P&L
- `Total Gain %` - P&L percentage
- `Value $` - Current value

### Step 7: Test the Setup

```bash
# Test market summary
python daily_market_summary.py --test

# Test with live data
python daily_market_summary.py

# Test with timing modes
python daily_market_summary.py --timing morning
python daily_market_summary.py --timing close
```

### Step 8: Configure Windows Task Scheduler

Open PowerShell as Administrator:

```powershell
# Calendar update at 6:00 AM
$action = New-ScheduledTaskAction `
    -Execute "C:\Users\YOUR_USER\AppData\Local\Programs\Python\Python312\python.exe" `
    -Argument "C:\scripts\investment-summary\calendar_sync.py --update-all" `
    -WorkingDirectory "C:\scripts\investment-summary"

$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName "Investment Calendar Update" `
    -Action $action -Trigger $trigger -Principal $principal `
    -Description "Updates Google Calendar with latest options P&L"
```

### Step 9: Set Up n8n Workflow

1. Start n8n: `n8n start`
2. Create a new workflow with:
   - **Schedule Trigger**: 6:30 AM for morning, 1:00 PM for afternoon
   - **HTTP Request**: GET `http://localhost:8080/market-summary?timing=morning`
   - **Code Node**: Transform JSON to HTML email
   - **Gmail Node**: Send formatted email

Example n8n HTTP Request configuration:
```
URL: http://localhost:8080/market-summary?timing=morning
Method: GET
Response Format: JSON
```

---

## File Structure

```
investment-summary/
├── daily_market_summary.py   # Main script - fetches data, calculates P&L
├── load_portfolio.py         # Parses brokerage CSV exports
├── calendar_sync.py          # Google Calendar integration
├── serve.py                  # HTTP API server (port 8080)
├── README.md                 # This documentation
├── .gitignore                # Excludes private_data/, __pycache__/
│
└── private_data/             # Git-ignored sensitive files
    ├── portfolio.csv         # Brokerage portfolio export
    ├── google_credentials.json  # OAuth credentials
    └── token.json            # Auto-generated auth token
```

### File Descriptions

| File | Purpose |
|------|---------|
| `daily_market_summary.py` | Core script that fetches market data, calculates portfolio value, generates action recommendations, and supports morning/close timing modes |
| `load_portfolio.py` | Parses CSV exports from brokerages, handles both stock and options positions, calculates days to expiration |
| `calendar_sync.py` | Creates/updates Google Calendar events for options expirations with P&L data and reminders |
| `serve.py` | Simple HTTP server exposing the market summary as JSON API for n8n integration |

---

## Configuration

### Updating Portfolio Data

1. Export portfolio from your brokerage as CSV
2. Save to `private_data/portfolio.csv` (overwrites existing)
3. Next script run will use updated data

### Customizing Email Schedules

Modify n8n workflow triggers:
- Morning email: Change schedule trigger time (default 6:30 AM)
- Afternoon email: Change schedule trigger time (default 1:00 PM)

### Modifying Priority Thresholds

In `daily_market_summary.py`, adjust the `calculate_action_recommendations()` function:

```python
# Urgency levels based on combined score
if combined_score >= 90:      # CRITICAL threshold
    urgency_level = "CRITICAL"
elif combined_score >= 70:    # HIGH threshold
    urgency_level = "HIGH"
elif combined_score >= 50:    # MEDIUM threshold
    urgency_level = "MEDIUM"
else:
    urgency_level = "LOW"

# Profit-taking thresholds for short positions
if is_short and total_gain_percent >= 60:    # Take profit threshold
    recommended_action = "TAKE PROFIT NOW"
elif is_short and total_gain_percent >= 50:  # Consider closing threshold
    recommended_action = "CONSIDER CLOSING"
```

### Adding New Tracked Stocks

Edit the `STOCKS` list in `daily_market_summary.py`:

```python
STOCKS = [
    ("AAPL", "Apple Inc.", "aapl"),
    ("MSFT", "Microsoft Corporation", "msft"),
    # Add new stocks here:
    ("AMZN", "Amazon.com Inc.", "amzn"),
]
```

---

## Daily Automation Schedule

| Time | Task | Script/Service |
|------|------|----------------|
| 6:00 AM | Update calendar events with latest P&L | `calendar_sync.py --update-all` (Task Scheduler) |
| 6:30 AM | Send morning preview email | n8n workflow → `serve.py?timing=morning` |
| 1:00 PM | Send afternoon recap email | n8n workflow → `serve.py?timing=close` |

### Morning Preview Email Contains

- Pre-market S&P 500 futures trend (bullish/neutral/bearish)
- VIX level with interpretation
- Options expiring today
- Top 5 positions by priority score

### Afternoon Recap Email Contains

- Final S&P 500 and VIX performance
- Portfolio performance vs market
- Top 3 gainers and losers (by dollar amount)
- Options P&L summary with best/worst performers
- Positions needing attention tomorrow

---

## Usage

### Manual Testing

```bash
# Basic test with sample data
python daily_market_summary.py --test

# Live data fetch
python daily_market_summary.py

# Morning preview mode
python daily_market_summary.py --timing morning

# Market close recap mode
python daily_market_summary.py --timing close
```

### HTTP API

Start the server:
```bash
python serve.py
```

Endpoints:
```
GET http://localhost:8080/market-summary
GET http://localhost:8080/market-summary?timing=morning
GET http://localhost:8080/market-summary?timing=close
```

### Calendar Sync

```bash
# Preview changes (no actual updates)
python calendar_sync.py --create-all --dry-run

# Create events for all options
python calendar_sync.py --create-all

# Update existing events with latest data
python calendar_sync.py --update-all
```

### View Calendar Events

Open Google Calendar to see options expirations:
- Green events = profitable positions
- Red events = losing positions
- Reminders at 30 days, 7 days, and 1 day before expiration

### Run Scheduled Task Manually

```powershell
Start-ScheduledTask -TaskName "Investment Calendar Update"
```

---

## Troubleshooting

### API Errors

**Issue**: `yfinance` returns errors or empty data

**Solutions**:
1. Check internet connection
2. Verify ticker symbols are correct
3. Yahoo Finance may have rate limits - add delays between requests
4. Some symbols need mapping (e.g., `BRK.B` → `BRK-B`)

```python
# Symbol mapping in daily_market_summary.py
YFINANCE_SYMBOL_MAP = {
    "BRK.B": "BRK-B",
    "BRK.A": "BRK-A",
}
```

### Email Not Sending

**Issue**: n8n workflow fails to send email

**Solutions**:
1. Verify Gmail SMTP credentials in n8n
2. Enable "Less secure app access" or use App Password
3. Check n8n logs: `n8n start` in terminal shows errors
4. Verify `serve.py` is running: `curl http://localhost:8080/market-summary`

### Calendar Sync Issues

**Issue**: `calendar_sync.py` authentication fails

**Solutions**:
1. Delete `private_data/token.json` and re-authenticate
2. Verify `google_credentials.json` is valid
3. Check Google Cloud Console for API quota limits
4. Ensure Calendar API is enabled in project

**Issue**: Events not appearing in calendar

**Solutions**:
1. Check you're looking at the primary calendar
2. Verify timezone settings (default: America/New_York)
3. Run with `--dry-run` first to preview changes

### serve.py Not Running

**Issue**: HTTP server won't start

**Solutions**:
1. Check if port 8080 is already in use: `netstat -ano | findstr 8080`
2. Run as administrator if permission denied
3. Check for Python errors in console output

**Issue**: Scheduled task fails with "File not found"

**Solutions**:
1. Use full path to Python executable
2. Verify working directory is set correctly
3. Check task history in Task Scheduler for detailed errors

```powershell
# Find Python path
(Get-Command python).Source
```

---

## Extension Ideas

### Additional Data Sources

- **Alpha Vantage**: Alternative to Yahoo Finance with more reliable API
- **IEX Cloud**: Professional-grade market data
- **Polygon.io**: Real-time and historical data
- **Earnings Calendar**: Track upcoming earnings for holdings

### Notification Channels

- **Slack**: Send alerts via Slack webhook
- **Telegram**: Mobile notifications via bot
- **Discord**: Community server updates
- **SMS**: Twilio for critical alerts

### Mobile App

- **Home Assistant**: Dashboard widget for portfolio
- **iOS Shortcuts**: Quick view via Siri
- **Tasker (Android)**: Automated mobile alerts

### Historical Tracking

- **SQLite Database**: Store daily snapshots
- **Grafana Dashboard**: Visualize performance over time
- **Weekly/Monthly Reports**: Aggregate performance summaries

### Advanced Features

- **Dividend Tracking**: Monitor upcoming dividends
- **Tax Lot Tracking**: Cost basis and wash sale detection
- **Sector Allocation**: Portfolio diversification analysis
- **Risk Metrics**: Beta, Sharpe ratio, max drawdown

---

## Key Learnings and Best Practices

### Python/n8n Integration Patterns

1. **JSON as Interface**: Python outputs JSON to stdout, n8n consumes via HTTP
2. **Stateless Design**: Each script run is independent, no shared state
3. **Error Handling**: Return structured error responses, not exceptions
4. **Timeout Configuration**: Set reasonable timeouts (30s) for HTTP requests

```python
# Structured error response pattern
try:
    data = fetch_market_data()
    print(json.dumps(data, indent=2))
except Exception as e:
    error_response = {
        "status": "error",
        "error": str(e),
        "timestamp": datetime.now().isoformat()
    }
    print(json.dumps(error_response, indent=2))
    sys.exit(1)
```

### API Authentication

1. **Credentials Separation**: Keep OAuth credentials in git-ignored directory
2. **Token Refresh**: Handle expired tokens gracefully
3. **Scope Minimization**: Request only needed permissions
4. **Error Messages**: Provide clear instructions when credentials missing

### Error Handling

1. **Graceful Degradation**: Continue with partial data if one API fails
2. **Detailed Logging**: Include timestamps and context in error messages
3. **Exit Codes**: Use non-zero exit codes for failures
4. **Validation**: Check for required data before processing

### Git-Ignored Private Data

Essential entries for `.gitignore`:
```
private_data/
__pycache__/
*.pyc
.env
token.json
```

**Why this matters**:
- Portfolio data is sensitive financial information
- API credentials must never be committed
- Token files contain refresh tokens that grant access

### Code Organization

1. **Section Comments**: Use clear headers to organize code sections
2. **Configuration at Top**: Keep tunable values near the top of files
3. **Main Entry Point**: Use `if __name__ == "__main__":` pattern
4. **Separate Concerns**: Portfolio loading, API calls, calculations in separate functions

---

## License

This project is for personal use. Adapt freely for your own portfolio tracking needs.

---

## Contributing

This is a personal project, but feel free to fork and adapt for your own use. If you build something interesting, consider sharing your extensions!
