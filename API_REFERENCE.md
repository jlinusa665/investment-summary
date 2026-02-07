# API Reference

Investment Portfolio Tracker HTTP API Documentation

## Base URL

```
http://localhost:8080
```

**Default Port:** 8080

**Protocol:** HTTP (HTTPS not configured by default)

---

## Authentication

No authentication required. The API is designed for local network access only.

**Security Note:** Do not expose this API to the public internet without adding authentication.

---

## Endpoints

### GET /market-summary

Retrieves comprehensive market data, portfolio valuations, options analysis, and action recommendations.

#### Query Parameters

| Parameter | Type | Required | Values | Description |
|-----------|------|----------|--------|-------------|
| `timing` | string | No | `morning`, `close` | Timing mode for specialized reports |

#### Request Examples

**Default Mode (no timing parameter):**
```bash
curl http://localhost:8080/market-summary
```

**Morning Preview Mode:**
```bash
curl "http://localhost:8080/market-summary?timing=morning"
```

**Market Close Mode:**
```bash
curl "http://localhost:8080/market-summary?timing=close"
```

---

## Response Format

### Content Type

```
Content-Type: application/json
```

### CORS Headers

```
Access-Control-Allow-Origin: *
```

---

## Response Schema

### Base Response (All Modes)

```json
{
  "timestamp": "string (ISO 8601)",
  "status": "string",
  "mode": "string",
  "indices": { ... },
  "stocks": { ... },
  "portfolio": { ... },
  "options": { ... },
  "action_recommendations": { ... }
}
```

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp of data generation |
| `status` | string | `"success"`, `"partial_failure"`, or `"error"` |
| `mode` | string | `"live"` or `"test"` |
| `summary_type` | string | Present only with timing parameter: `"morning_preview"` or `"market_close"` |
| `errors` | array | Present only when `status` is `"partial_failure"` |

---

### indices Object

Market index data for S&P 500 and VIX.

```json
{
  "indices": {
    "sp500": {
      "symbol": "^GSPC",
      "name": "S&P 500",
      "current_price": 5021.84,
      "previous_close": 4997.91,
      "daily_change_percent": 0.48
    },
    "vix": {
      "symbol": "^VIX",
      "name": "CBOE Volatility Index",
      "current_price": 14.32,
      "previous_close": 14.85,
      "daily_change_percent": -3.57
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Ticker symbol |
| `name` | string | Human-readable name |
| `current_price` | number | Current/last price |
| `previous_close` | number | Previous trading day close |
| `daily_change_percent` | number | Percentage change from previous close |
| `error` | string | Present instead of price data if fetch failed |

---

### stocks Object

Individual stock data for tracked symbols.

```json
{
  "stocks": {
    "aapl": {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "current_price": 185.92,
      "previous_close": 184.40,
      "daily_change_percent": 0.82
    }
  }
}
```

**Keys:** Lowercase ticker symbol (e.g., `"aapl"`, `"msft"`)

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Original ticker symbol |
| `name` | string | Company name |
| `current_price` | number | Current/last price |
| `previous_close` | number | Previous trading day close |
| `daily_change_percent` | number | Percentage change |
| `error` | string | Present if fetch failed for this ticker |

---

### portfolio Object

Aggregated portfolio valuation and per-stock holdings.

```json
{
  "portfolio": {
    "total_portfolio_value": 73498.40,
    "total_portfolio_change_dollars": 679.55,
    "total_portfolio_change_percent": 0.93,
    "per_stock_holdings": {
      "aapl": {
        "symbol": "AAPL",
        "shares": 100,
        "current_value": 18592.00,
        "daily_change_dollars": 152.00
      }
    }
  }
}
```

#### Portfolio Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_portfolio_value` | number | Sum of all stock holdings at current prices |
| `total_portfolio_change_dollars` | number | Total dollar change from previous close |
| `total_portfolio_change_percent` | number | Percentage change from previous close |

#### Per-Stock Holding Fields

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Stock ticker |
| `shares` | integer | Number of shares held |
| `current_value` | number | Current market value (shares × price) |
| `daily_change_dollars` | number | Dollar change for this position today |

---

### options Object

Options portfolio summary and individual positions.

```json
{
  "options": {
    "total_options_value": 5250.00,
    "total_options_change_dollars": 125.50,
    "total_options_change_percent": 2.45,
    "options_positions": [ ... ],
    "expiring_soon": [ ... ],
    "long_positions_summary": {
      "count": 2,
      "total_value": 3500.00
    },
    "short_positions_summary": {
      "count": 3,
      "total_value": 1750.00
    }
  }
}
```

#### Options Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_options_value` | number | Total current value of all options |
| `total_options_change_dollars` | number | Total dollar change today |
| `total_options_change_percent` | number | Percentage change today |
| `options_positions` | array | Full list of option positions |
| `expiring_soon` | array | Positions expiring within 7 days |
| `long_positions_summary` | object | Aggregate of long positions |
| `short_positions_summary` | object | Aggregate of short positions |

#### Option Position Object

```json
{
  "symbol": "AAPL250207C00190000",
  "underlying_symbol": "AAPL",
  "expiration_date": "2025-02-07",
  "strike_price": 190.00,
  "option_type": "Call",
  "days_to_expiration": 0,
  "quantity": -1,
  "is_short": true,
  "position_type": "short",
  "price_paid": 12.50,
  "current_price": 8.50,
  "days_gain": 75.00,
  "total_gain": 425.00,
  "total_gain_percent": 33.30,
  "current_value": -850.00
}
```

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Full option symbol |
| `underlying_symbol` | string | Underlying stock ticker |
| `expiration_date` | string | Expiration date (YYYY-MM-DD) |
| `strike_price` | number | Strike price |
| `option_type` | string | `"Call"` or `"Put"` |
| `days_to_expiration` | integer | Days until expiration (0 = today) |
| `quantity` | integer | Contract quantity (negative = short) |
| `is_short` | boolean | `true` if short position |
| `position_type` | string | `"long"` or `"short"` |
| `price_paid` | number | Original purchase price per contract |
| `current_price` | number | Current price per contract |
| `days_gain` | number | Dollar gain/loss today |
| `total_gain` | number | Total dollar gain/loss |
| `total_gain_percent` | number | Total percentage gain/loss |
| `current_value` | number | Current market value (negative for shorts) |

---

### action_recommendations Object

Prioritized action recommendations for options positions.

```json
{
  "action_recommendations": {
    "profit_taking_opportunities": [ ... ],
    "urgent_losses": [ ... ],
    "expiring_this_week": [ ... ],
    "expiring_next_week": [ ... ],
    "all_positions_by_priority": [ ... ]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `profit_taking_opportunities` | array | Short positions with ≥50% profit |
| `urgent_losses` | array | Positions with priority score ≥70 or expiring within 7 days with losses |
| `expiring_this_week` | array | All positions expiring within 7 days |
| `expiring_next_week` | array | All positions expiring within 14 days |
| `all_positions_by_priority` | array | All positions sorted by combined priority score (descending) |

#### Scored Position Object

```json
{
  "symbol": "MSFT250214P00400000",
  "underlying_symbol": "MSFT",
  "days_to_expiration": 1,
  "expiration_date": "2025-02-14",
  "current_value": 1200.00,
  "total_gain": -300.00,
  "total_gain_percent": -20.0,
  "position_type": "Put",
  "is_short": false,
  "time_urgency_score": 100.00,
  "loss_dollar_score": 75.00,
  "loss_percent_score": 20.00,
  "combined_priority_score": 85.00,
  "urgency_level": "HIGH",
  "recommended_action": "HIGH PRIORITY - Consider closing to stop losses",
  "cost_to_close": 1200.00
}
```

#### Priority Scoring Fields

| Field | Type | Description |
|-------|------|-------------|
| `time_urgency_score` | number | 0-100 score based on days to expiration |
| `loss_dollar_score` | number | 0-100 score based on dollar loss relative to max loss |
| `loss_percent_score` | number | 0-100 score based on percentage loss |
| `combined_priority_score` | number | Weighted average: time×0.4 + loss_dollar×0.3 + loss_percent×0.3 |
| `urgency_level` | string | `"CRITICAL"` (≥90), `"HIGH"` (≥70), `"MEDIUM"` (≥50), `"LOW"` (<50) |
| `recommended_action` | string | Human-readable action recommendation |
| `cost_to_close` | number | Absolute value to close position |

---

## Timing Modes

### Morning Preview (`?timing=morning`)

Adds `summary_type` and `market_preview` to response.

```json
{
  "summary_type": "morning_preview",
  "market_preview": {
    "sp500_futures": {
      "symbol": "ES=F",
      "name": "S&P 500 E-mini Futures",
      "current_price": 5025.50,
      "previous_close": 5010.25,
      "change": 15.25,
      "change_percent": 0.30,
      "trend": "bullish"
    },
    "vix_premarket": {
      "symbol": "^VIX",
      "name": "CBOE Volatility Index",
      "current_level": 14.50,
      "interpretation": "low_volatility",
      "previous_close": 14.85,
      "change": -0.35
    },
    "todays_expirations": [ ... ],
    "todays_expirations_count": 1,
    "key_positions_to_watch": [ ... ]
  }
}
```

#### market_preview Fields

| Field | Type | Description |
|-------|------|-------------|
| `sp500_futures` | object | Pre-market S&P 500 futures data |
| `vix_premarket` | object | Pre-market VIX level |
| `todays_expirations` | array | Options expiring today (days_to_expiration = 0) |
| `todays_expirations_count` | integer | Count of today's expirations |
| `key_positions_to_watch` | array | Top 5 positions by priority score |

#### Futures Trend Values

| Value | Condition |
|-------|-----------|
| `"bullish"` | change_percent > 0.3% |
| `"bearish"` | change_percent < -0.3% |
| `"neutral"` | -0.3% ≤ change_percent ≤ 0.3% |

#### VIX Interpretation Values

| Value | VIX Level |
|-------|-----------|
| `"low_volatility"` | < 15 |
| `"normal"` | 15-20 |
| `"elevated"` | 20-30 |
| `"high_volatility"` | > 30 |

---

### Market Close (`?timing=close`)

Adds `summary_type` and `market_recap` to response.

```json
{
  "summary_type": "market_close",
  "market_recap": {
    "market_performance": {
      "sp500": {
        "close": 5021.84,
        "change_percent": 0.48,
        "direction": "up"
      },
      "vix": {
        "close": 14.32,
        "change_percent": -3.57
      }
    },
    "portfolio_vs_market": {
      "portfolio_change_percent": 0.93,
      "sp500_change_percent": 0.48,
      "relative_performance": 0.45,
      "outperformed": true
    },
    "top_gainers": [ ... ],
    "top_losers": [ ... ],
    "options_summary": {
      "total_options_pnl": 125.50,
      "total_options_pnl_percent": 2.45,
      "best_performing": {
        "symbol": "NVDA250221C00700000",
        "days_gain": 200.50
      },
      "worst_performing": {
        "symbol": "MSFT250214P00400000",
        "days_gain": -150.00
      }
    },
    "positions_needing_attention_tomorrow": [ ... ]
  }
}
```

#### market_recap Fields

| Field | Type | Description |
|-------|------|-------------|
| `market_performance` | object | S&P 500 and VIX closing data |
| `portfolio_vs_market` | object | Portfolio performance comparison |
| `top_gainers` | array | Top 3 stock holdings by daily dollar gain |
| `top_losers` | array | Bottom 3 stock holdings by daily dollar loss |
| `options_summary` | object | Options P&L summary with best/worst |
| `positions_needing_attention_tomorrow` | array | Options expiring in 1 day or with high priority |

#### portfolio_vs_market Fields

| Field | Type | Description |
|-------|------|-------------|
| `portfolio_change_percent` | number | Portfolio's percentage change today |
| `sp500_change_percent` | number | S&P 500's percentage change today |
| `relative_performance` | number | Difference (portfolio - S&P 500) |
| `outperformed` | boolean | `true` if portfolio beat S&P 500 |

---

## Error Responses

### HTTP 200 with Error Status

When data fetch partially fails:

```json
{
  "timestamp": "2026-02-06T14:30:00.000000",
  "status": "partial_failure",
  "mode": "live",
  "errors": [
    "Apple Inc.: Could not retrieve price data",
    "NVIDIA Corporation: Network timeout"
  ],
  "indices": { ... },
  "stocks": { ... }
}
```

### HTTP 200 with Complete Failure

When the script encounters an exception:

```json
{
  "timestamp": "2026-02-06T14:30:00.000000",
  "status": "error",
  "error": "Portfolio file not found"
}
```

### HTTP 500 Internal Server Error

When serve.py encounters an exception:

```json
{
  "error": "Detailed error message"
}
```

### HTTP 404 Not Found

When requesting an invalid endpoint:

```
(empty response body)
```

---

## Error Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"error"` or `"partial_failure"` |
| `error` | string | Single error message (complete failure) |
| `errors` | array | List of error messages (partial failure) |

---

## Rate Limiting

**No rate limiting implemented.**

However, be aware of upstream limits:
- **Yahoo Finance (yfinance):** Unofficial API, may rate limit aggressive requests
- **Recommended:** Wait at least 1 second between requests
- **Typical response time:** 2-5 seconds (depends on number of tickers)

---

## Timeout

**Server timeout:** 30 seconds

If the upstream Yahoo Finance API is slow, requests may timeout after 30 seconds.

---

## Example Requests & Responses

### Example 1: Default Request

**Request:**
```bash
curl -s http://localhost:8080/market-summary | jq '.status, .portfolio.total_portfolio_value'
```

**Response:**
```json
"success"
73498.4
```

---

### Example 2: Morning Preview

**Request:**
```bash
curl -s "http://localhost:8080/market-summary?timing=morning" | jq '.summary_type, .market_preview.sp500_futures.trend'
```

**Response:**
```json
"morning_preview"
"bullish"
```

---

### Example 3: Market Close with Portfolio Comparison

**Request:**
```bash
curl -s "http://localhost:8080/market-summary?timing=close" | jq '.market_recap.portfolio_vs_market'
```

**Response:**
```json
{
  "portfolio_change_percent": 0.93,
  "sp500_change_percent": 0.48,
  "relative_performance": 0.45,
  "outperformed": true
}
```

---

### Example 4: Get Today's Expirations

**Request:**
```bash
curl -s "http://localhost:8080/market-summary?timing=morning" | jq '.market_preview.todays_expirations[] | {symbol: .underlying_symbol, strike: .strike_price, type: .position_type}'
```

**Response:**
```json
{
  "symbol": "AAPL",
  "strike": 190,
  "type": "Call"
}
```

---

### Example 5: Get High Priority Actions

**Request:**
```bash
curl -s http://localhost:8080/market-summary | jq '.action_recommendations.urgent_losses[] | {symbol: .symbol, urgency: .urgency_level, action: .recommended_action}'
```

**Response:**
```json
{
  "symbol": "MSFT250214P00400000",
  "urgency": "HIGH",
  "action": "HIGH PRIORITY - Consider closing to stop losses"
}
```

---

## Code Examples

### Python

```python
import requests

response = requests.get(
    "http://localhost:8080/market-summary",
    params={"timing": "morning"},
    timeout=30
)
data = response.json()

print(f"Status: {data['status']}")
print(f"Futures trend: {data['market_preview']['sp500_futures']['trend']}")
print(f"Expirations today: {data['market_preview']['todays_expirations_count']}")
```

### JavaScript (Node.js)

```javascript
const fetch = require('node-fetch');

async function getMarketSummary(timing = null) {
  const url = new URL('http://localhost:8080/market-summary');
  if (timing) url.searchParams.set('timing', timing);

  const response = await fetch(url, { timeout: 30000 });
  return response.json();
}

// Usage
const data = await getMarketSummary('close');
console.log(`Portfolio: ${data.market_recap.portfolio_vs_market.outperformed ? 'beat' : 'lagged'} market`);
```

### PowerShell

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8080/market-summary?timing=close" -TimeoutSec 30

Write-Host "Portfolio Value: $($response.portfolio.total_portfolio_value)"
Write-Host "Daily Change: $($response.portfolio.total_portfolio_change_dollars)"
Write-Host "Outperformed S&P: $($response.market_recap.portfolio_vs_market.outperformed)"
```

---

## Server Management

### Start Server

```bash
python serve.py
```

**Output:**
```
Market Summary API running on http://localhost:8080
Endpoints:
  http://localhost:8080/market-summary
  http://localhost:8080/market-summary?timing=morning
  http://localhost:8080/market-summary?timing=close
```

### Run in Background (Windows)

```powershell
Start-Process pythonw -ArgumentList "C:\scripts\investment-summary\serve.py" -WindowStyle Hidden
```

### Check if Running

```bash
curl -s http://localhost:8080/market-summary | jq '.status'
```

### Stop Server

Find and kill the Python process:
```powershell
Get-Process python* | Where-Object { $_.Path -like "*serve.py*" } | Stop-Process
```
