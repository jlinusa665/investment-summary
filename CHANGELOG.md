# Changelog

All notable changes to the Investment Portfolio Tracker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Template for future additions)

### Changed
- (Template for future changes)

### Fixed
- (Template for future fixes)

### Removed
- (Template for future removals)

---

## [1.0.0] - 2026-02-06

### Added

#### Core Portfolio Tracking
- `daily_market_summary.py` - Main script for fetching market data and portfolio valuations
- Real-time stock price fetching via Yahoo Finance (yfinance)
- S&P 500 and VIX index tracking with daily change percentages
- Portfolio valuation with total value, daily P&L dollars, and percentage change
- Per-stock holdings breakdown with individual position values

#### CSV Portfolio Loading
- `load_portfolio.py` - Parses brokerage CSV exports
- Support for standard stock positions with quantity tracking
- Automatic filtering of CASH and TOTAL rows
- Symbol mapping for special tickers (BRK.B → BRK-B)
- Fallback to mock portfolio data when CSV not available

#### Options Tracking
- Full options contract parsing from CSV exports
- Support for option symbol format: "NVDA Feb 27 '26 $195 Call"
- Automatic expiration date calculation and days-to-expiration countdown
- Long vs short position detection via quantity sign
- P&L tracking: current value, day's gain, total gain (dollars and percent)
- Expiring soon alerts for positions within 7 days

#### Action Recommendations Engine
- Priority scoring algorithm with three components:
  - Time urgency score (0-100) based on days to expiration
  - Loss dollar score (0-100) relative to maximum portfolio loss
  - Loss percent score (0-100) based on percentage decline
- Combined priority score: time×0.4 + loss_dollar×0.3 + loss_percent×0.3
- Four urgency levels: CRITICAL (≥90), HIGH (≥70), MEDIUM (≥50), LOW (<50)
- Profit-taking recommendations for short positions at 50%+ gain
- Categorized lists: profit opportunities, urgent losses, expiring this/next week

#### Timing Modes for Daily Reports
- `--timing morning` flag for pre-market preview:
  - S&P 500 E-mini futures with trend indicator (bullish/neutral/bearish)
  - Pre-market VIX level with interpretation
  - Today's expirations list (days_to_expiration = 0)
  - Top 5 key positions to watch by priority
- `--timing close` flag for end-of-day recap:
  - Final market performance summary
  - Portfolio vs S&P 500 comparison with outperformance indicator
  - Top 3 gainers and losers by dollar amount
  - Options summary with best/worst performers
  - Positions needing attention tomorrow

#### HTTP API Server
- `serve.py` - Simple HTTP server on port 8080
- GET `/market-summary` endpoint returning JSON
- Query parameter support: `?timing=morning` and `?timing=close`
- CORS headers for cross-origin requests
- 30-second timeout for upstream API calls

#### Google Calendar Integration
- `calendar_sync.py` - Syncs options expirations to Google Calendar
- OAuth 2.0 authentication with token persistence
- Calendar event creation with expiration date and time
- Color-coded events: green (profitable) / red (losing)
- Multiple reminders: 30 days, 7 days, 1 day before expiration
- Event descriptions with full P&L data and action recommendations
- `--create-all` and `--update-all` modes
- `--dry-run` flag for previewing changes

#### Windows Task Scheduler Integration
- Scheduled task for daily calendar updates at 6:00 AM
- PowerShell commands for task creation and management
- Support for running at user logon

#### Documentation
- `README.md` - Comprehensive project documentation (602 lines)
  - System architecture diagram
  - Prerequisites and installation guide
  - File structure and configuration
  - Troubleshooting section
  - Extension ideas
- `QUICK_START.md` - 5-minute setup guide for experienced users
- `N8N_WORKFLOWS.md` - Complete n8n workflow documentation (825 lines)
  - Morning and afternoon workflow configurations
  - Full JavaScript code for email formatting
  - SMTP/Gmail setup instructions
  - Common errors and fixes
- `API_REFERENCE.md` - HTTP API documentation (728 lines)
  - Complete JSON response schema
  - All fields documented with types
  - Example requests with jq queries
  - Code examples in Python, JavaScript, PowerShell

#### Project Infrastructure
- `.gitignore` for Python artifacts, virtual environments, and private data
- `private_data/` directory structure for sensitive files
- Test mode (`--test` flag) with sample data for development

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2026-02-06 | Initial release with full feature set |

---

## Upgrade Guide

### Upgrading to Future Versions

1. Pull latest changes:
   ```bash
   git pull origin master
   ```

2. Install any new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check CHANGELOG for breaking changes

4. Update n8n workflows if Code node changes

5. Re-run calendar sync if event format changed:
   ```bash
   python calendar_sync.py --update-all
   ```

---

## Links

- [Repository](https://github.com/jlinusa665/investment-summary)
- [README](README.md)
- [Quick Start](QUICK_START.md)
- [API Reference](API_REFERENCE.md)
- [n8n Workflows](N8N_WORKFLOWS.md)

[Unreleased]: https://github.com/jlinusa665/investment-summary/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jlinusa665/investment-summary/releases/tag/v1.0.0
