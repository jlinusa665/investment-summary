# Quick Start Guide

Get the Investment Portfolio Tracker running in 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.10+
- [ ] Git
- [ ] Google account
- [ ] Brokerage CSV export of your portfolio

## 1. Install Dependencies

```bash
pip install yfinance google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 2. Clone & Setup

```bash
git clone https://github.com/jlinusa665/investment-summary.git
cd investment-summary
mkdir private_data
```

## 3. Google Calendar API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable **Google Calendar API**
3. **Credentials** → **Create OAuth client ID** → **Desktop app**
4. Download JSON → Save as `private_data/google_credentials.json`
5. Run to authenticate:
   ```bash
   python calendar_sync.py --create-all --dry-run
   ```
6. Approve in browser → `token.json` is created automatically

## 4. Portfolio Configuration

Save your brokerage export as `private_data/portfolio.csv`.

**Required columns:**
```
Symbol,Quantity,Last Price $,Day's Gain $,Total Gain $,Total Gain %,Value $
```

**Example:**
```csv
Symbol,Quantity,Last Price $,Day's Gain $,Total Gain $,Total Gain %,Value $
AAPL,100,185.50,152.00,1250.00,7.25,18550.00
NVDA Feb 27 '26 $195 Call,-1,8.50,75.00,425.00,33.30,-850.00
```

## 5. Test It

```bash
# Sample data test
python daily_market_summary.py --test

# Live data
python daily_market_summary.py

# Morning preview
python daily_market_summary.py --timing morning

# Market close recap
python daily_market_summary.py --timing close
```

## 6. Start HTTP Server

```bash
python serve.py
```

Endpoints:
- `http://localhost:8080/market-summary`
- `http://localhost:8080/market-summary?timing=morning`
- `http://localhost:8080/market-summary?timing=close`

## 7. Sync to Calendar

```bash
# Preview first
python calendar_sync.py --create-all --dry-run

# Create events
python calendar_sync.py --create-all
```

## Quick Test Commands

```bash
# Verify portfolio loads
python load_portfolio.py

# Check HTTP API
curl http://localhost:8080/market-summary

# Test calendar update
python calendar_sync.py --update-all --dry-run
```

## Next Steps

- See [README.md](README.md) for:
  - n8n email workflow setup
  - Windows Task Scheduler configuration
  - Customizing priority thresholds
  - Troubleshooting guide
  - Extension ideas
