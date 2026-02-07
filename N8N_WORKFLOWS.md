# n8n Workflow Documentation

Complete guide to setting up the morning and afternoon email workflows in n8n.

## Overview

| Workflow | Trigger Time | Purpose | API Endpoint |
|----------|--------------|---------|--------------|
| Morning Preview | 6:30 AM (Mon-Fri) | Pre-market briefing | `?timing=morning` |
| Afternoon Recap | 1:00 PM (Mon-Fri) | End-of-day summary | `?timing=close` |

Both workflows follow the same pattern:
```
Schedule Trigger → HTTP Request → Code (Format HTML) → Send Email
```

---

## Morning Preview Workflow

### Node 1: Schedule Trigger

**Type:** Schedule Trigger

**Settings:**
| Field | Value |
|-------|-------|
| Trigger Interval | Custom (Cron) |
| Cron Expression | `30 6 * * 1-5` |

**Cron Breakdown:**
- `30` - Minute 30
- `6` - Hour 6 (6:30 AM)
- `*` - Any day of month
- `*` - Any month
- `1-5` - Monday through Friday

---

### Node 2: HTTP Request

**Type:** HTTP Request

**Settings:**
| Field | Value |
|-------|-------|
| Method | GET |
| URL | `http://localhost:8080/market-summary` |
| Query Parameters | `timing` = `morning` |
| Response Format | JSON |
| Timeout | 30000 |

**Full URL:** `http://localhost:8080/market-summary?timing=morning`

---

### Node 3: Code (Format Morning Email)

**Type:** Code

**Settings:**
| Field | Value |
|-------|-------|
| Language | JavaScript |
| Mode | Run Once for All Items |

**Complete JavaScript Code:**

```javascript
// Morning Preview Email Formatter
const data = $input.first().json;

// Helper function to format currency
function formatCurrency(value) {
  if (value === null || value === undefined) return 'N/A';
  const num = parseFloat(value);
  const sign = num >= 0 ? '+' : '';
  return sign + '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Helper function to format percentage
function formatPercent(value) {
  if (value === null || value === undefined) return 'N/A';
  const num = parseFloat(value);
  const sign = num >= 0 ? '+' : '';
  return sign + num.toFixed(2) + '%';
}

// Helper function for trend emoji
function getTrendEmoji(trend) {
  if (trend === 'bullish') return '🟢 Bullish';
  if (trend === 'bearish') return '🔴 Bearish';
  return '🟡 Neutral';
}

// Helper function for VIX interpretation
function getVixInterpretation(interp) {
  const map = {
    'low_volatility': '🟢 Low Volatility',
    'normal': '🟡 Normal',
    'elevated': '🟠 Elevated',
    'high_volatility': '🔴 High Volatility'
  };
  return map[interp] || interp;
}

// Helper function for urgency badge
function getUrgencyBadge(level) {
  const colors = {
    'CRITICAL': '#dc3545',
    'HIGH': '#fd7e14',
    'MEDIUM': '#ffc107',
    'LOW': '#28a745'
  };
  return `<span style="background-color: ${colors[level] || '#6c757d'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">${level}</span>`;
}

const preview = data.market_preview || {};
const futures = preview.sp500_futures || {};
const vix = preview.vix_premarket || {};
const todaysExpirations = preview.todays_expirations || [];
const keyPositions = preview.key_positions_to_watch || [];

// Build HTML email
let html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
    h1 { color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }
    h2 { color: #555; margin-top: 30px; }
    .card { background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0; }
    .futures-up { color: #28a745; }
    .futures-down { color: #dc3545; }
    table { width: 100%; border-collapse: collapse; margin: 10px 0; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #e9ecef; }
    .positive { color: #28a745; }
    .negative { color: #dc3545; }
    .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
  </style>
</head>
<body>
  <h1>🌅 Morning Market Preview</h1>
  <p style="color: #666;">Generated: ${new Date().toLocaleString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>

  <h2>📈 Pre-Market Futures</h2>
  <div class="card">
    <table>
      <tr>
        <td><strong>S&P 500 Futures (ES)</strong></td>
        <td class="${futures.change >= 0 ? 'futures-up' : 'futures-down'}">
          ${futures.current_price?.toLocaleString() || 'N/A'}
          (${formatPercent(futures.change_percent)})
        </td>
        <td>${getTrendEmoji(futures.trend)}</td>
      </tr>
    </table>
  </div>

  <h2>📊 VIX Level</h2>
  <div class="card">
    <table>
      <tr>
        <td><strong>VIX</strong></td>
        <td>${vix.current_level?.toFixed(2) || 'N/A'}</td>
        <td>${getVixInterpretation(vix.interpretation)}</td>
      </tr>
    </table>
  </div>
`;

// Today's Expirations
if (todaysExpirations.length > 0) {
  html += `
  <h2>⚠️ Expiring TODAY (${todaysExpirations.length})</h2>
  <div class="card" style="background: #fff3cd;">
    <table>
      <tr>
        <th>Symbol</th>
        <th>Type</th>
        <th>P&L</th>
        <th>Action</th>
      </tr>
  `;

  for (const pos of todaysExpirations) {
    const pnlClass = pos.total_gain >= 0 ? 'positive' : 'negative';
    html += `
      <tr>
        <td><strong>${pos.underlying_symbol}</strong> $${pos.strike_price || ''} ${pos.position_type}</td>
        <td>${pos.is_short ? 'Short' : 'Long'}</td>
        <td class="${pnlClass}">${formatCurrency(pos.total_gain)} (${formatPercent(pos.total_gain_percent)})</td>
        <td>${getUrgencyBadge(pos.urgency_level)}</td>
      </tr>
    `;
  }

  html += `</table></div>`;
} else {
  html += `
  <h2>✅ No Options Expiring Today</h2>
  <div class="card" style="background: #d4edda;">
    <p>No positions expire today.</p>
  </div>
  `;
}

// Key Positions to Watch
if (keyPositions.length > 0) {
  html += `
  <h2>👀 Key Positions to Watch</h2>
  <table>
    <tr>
      <th>Position</th>
      <th>Days Left</th>
      <th>P&L</th>
      <th>Priority</th>
    </tr>
  `;

  for (const pos of keyPositions) {
    const pnlClass = pos.total_gain >= 0 ? 'positive' : 'negative';
    html += `
      <tr>
        <td><strong>${pos.underlying_symbol}</strong> $${pos.strike_price || ''} ${pos.position_type}</td>
        <td>${pos.days_to_expiration} days</td>
        <td class="${pnlClass}">${formatCurrency(pos.total_gain)}</td>
        <td>${getUrgencyBadge(pos.urgency_level)}</td>
      </tr>
    `;
  }

  html += `</table>`;
}

html += `
  <div class="footer">
    <p>This is an automated morning briefing. Markets open at 9:30 AM ET.</p>
  </div>
</body>
</html>
`;

return [{
  json: {
    subject: `🌅 Morning Preview - ${futures.trend === 'bullish' ? '📈' : futures.trend === 'bearish' ? '📉' : '➡️'} Futures ${formatPercent(futures.change_percent)} | ${todaysExpirations.length} Expiring Today`,
    html: html
  }
}];
```

---

### Node 4: Send Email

**Type:** Send Email (or Gmail)

**Settings:**
| Field | Value |
|-------|-------|
| From Email | `your-email@gmail.com` |
| To Email | `your-email@gmail.com` |
| Subject | `{{ $json.subject }}` |
| HTML | `{{ $json.html }}` |

**SMTP Settings (if using Send Email node):**
| Field | Value |
|-------|-------|
| Host | `smtp.gmail.com` |
| Port | 587 |
| SSL/TLS | STARTTLS |
| User | `your-email@gmail.com` |
| Password | App Password (not regular password) |

---

## Afternoon Recap Workflow

### Node 1: Schedule Trigger

**Type:** Schedule Trigger

**Settings:**
| Field | Value |
|-------|-------|
| Trigger Interval | Custom (Cron) |
| Cron Expression | `0 13 * * 1-5` |

**Cron Breakdown:**
- `0` - Minute 0
- `13` - Hour 13 (1:00 PM)
- `*` - Any day of month
- `*` - Any month
- `1-5` - Monday through Friday

---

### Node 2: HTTP Request

**Type:** HTTP Request

**Settings:**
| Field | Value |
|-------|-------|
| Method | GET |
| URL | `http://localhost:8080/market-summary` |
| Query Parameters | `timing` = `close` |
| Response Format | JSON |
| Timeout | 30000 |

**Full URL:** `http://localhost:8080/market-summary?timing=close`

---

### Node 3: Code (Format Afternoon Email)

**Type:** Code

**Settings:**
| Field | Value |
|-------|-------|
| Language | JavaScript |
| Mode | Run Once for All Items |

**Complete JavaScript Code:**

```javascript
// Afternoon Recap Email Formatter
const data = $input.first().json;

// Helper functions
function formatCurrency(value) {
  if (value === null || value === undefined) return 'N/A';
  const num = parseFloat(value);
  const sign = num >= 0 ? '+' : '';
  return sign + '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatPercent(value) {
  if (value === null || value === undefined) return 'N/A';
  const num = parseFloat(value);
  const sign = num >= 0 ? '+' : '';
  return sign + num.toFixed(2) + '%';
}

function getUrgencyBadge(level) {
  const colors = {
    'CRITICAL': '#dc3545',
    'HIGH': '#fd7e14',
    'MEDIUM': '#ffc107',
    'LOW': '#28a745'
  };
  return `<span style="background-color: ${colors[level] || '#6c757d'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">${level}</span>`;
}

const recap = data.market_recap || {};
const marketPerf = recap.market_performance || {};
const portfolioVsMarket = recap.portfolio_vs_market || {};
const topGainers = recap.top_gainers || [];
const topLosers = recap.top_losers || [];
const optionsSummary = recap.options_summary || {};
const attentionTomorrow = recap.positions_needing_attention_tomorrow || [];
const portfolio = data.portfolio || {};

const sp500 = marketPerf.sp500 || {};
const vix = marketPerf.vix || {};

// Determine overall market direction
const marketEmoji = sp500.direction === 'up' ? '📈' : '📉';
const portfolioEmoji = portfolioVsMarket.outperformed ? '🏆' : '📊';

let html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
    h1 { color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }
    h2 { color: #555; margin-top: 30px; }
    .card { background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0; }
    .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .summary-box { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center; }
    .summary-box h3 { margin: 0 0 10px 0; font-size: 14px; color: #666; }
    .summary-box .value { font-size: 24px; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin: 10px 0; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #e9ecef; }
    .positive { color: #28a745; }
    .negative { color: #dc3545; }
    .outperformed { background: #d4edda; }
    .underperformed { background: #f8d7da; }
    .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
  </style>
</head>
<body>
  <h1>🌆 Market Close Recap</h1>
  <p style="color: #666;">Generated: ${new Date().toLocaleString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>

  <h2>${marketEmoji} Market Performance</h2>
  <div class="summary-grid">
    <div class="summary-box">
      <h3>S&P 500</h3>
      <div class="value ${sp500.change_percent >= 0 ? 'positive' : 'negative'}">${formatPercent(sp500.change_percent)}</div>
      <div style="color: #666; font-size: 14px;">${sp500.close?.toLocaleString() || 'N/A'}</div>
    </div>
    <div class="summary-box">
      <h3>VIX</h3>
      <div class="value ${vix.change_percent <= 0 ? 'positive' : 'negative'}">${formatPercent(vix.change_percent)}</div>
      <div style="color: #666; font-size: 14px;">${vix.close?.toFixed(2) || 'N/A'}</div>
    </div>
  </div>

  <h2>${portfolioEmoji} Portfolio vs Market</h2>
  <div class="card ${portfolioVsMarket.outperformed ? 'outperformed' : 'underperformed'}">
    <table>
      <tr>
        <td><strong>Your Portfolio</strong></td>
        <td class="${portfolioVsMarket.portfolio_change_percent >= 0 ? 'positive' : 'negative'}" style="font-size: 18px; font-weight: bold;">
          ${formatPercent(portfolioVsMarket.portfolio_change_percent)}
        </td>
      </tr>
      <tr>
        <td><strong>S&P 500</strong></td>
        <td class="${portfolioVsMarket.sp500_change_percent >= 0 ? 'positive' : 'negative'}">
          ${formatPercent(portfolioVsMarket.sp500_change_percent)}
        </td>
      </tr>
      <tr>
        <td><strong>Relative Performance</strong></td>
        <td class="${portfolioVsMarket.relative_performance >= 0 ? 'positive' : 'negative'}">
          ${formatPercent(portfolioVsMarket.relative_performance)} ${portfolioVsMarket.outperformed ? '✅' : ''}
        </td>
      </tr>
    </table>
    <p style="margin: 10px 0 0 0; text-align: center;">
      <strong>Portfolio Value:</strong> $${portfolio.total_portfolio_value?.toLocaleString() || 'N/A'}
      (${formatCurrency(portfolio.total_portfolio_change_dollars)})
    </p>
  </div>
`;

// Top Gainers
if (topGainers.length > 0) {
  html += `
  <h2>🚀 Top Gainers</h2>
  <table>
    <tr>
      <th>Symbol</th>
      <th>Shares</th>
      <th>Value</th>
      <th>Day's Gain</th>
    </tr>
  `;

  for (const stock of topGainers) {
    html += `
      <tr>
        <td><strong>${stock.symbol}</strong></td>
        <td>${stock.shares}</td>
        <td>$${stock.current_value?.toLocaleString() || 'N/A'}</td>
        <td class="positive">${formatCurrency(stock.daily_change_dollars)}</td>
      </tr>
    `;
  }

  html += `</table>`;
}

// Top Losers
if (topLosers.length > 0) {
  html += `
  <h2>📉 Top Losers</h2>
  <table>
    <tr>
      <th>Symbol</th>
      <th>Shares</th>
      <th>Value</th>
      <th>Day's Loss</th>
    </tr>
  `;

  for (const stock of topLosers) {
    html += `
      <tr>
        <td><strong>${stock.symbol}</strong></td>
        <td>${stock.shares}</td>
        <td>$${stock.current_value?.toLocaleString() || 'N/A'}</td>
        <td class="negative">${formatCurrency(stock.daily_change_dollars)}</td>
      </tr>
    `;
  }

  html += `</table>`;
}

// Options Summary
if (optionsSummary && optionsSummary.total_options_pnl !== undefined) {
  const optPnlClass = optionsSummary.total_options_pnl >= 0 ? 'positive' : 'negative';

  html += `
  <h2>📋 Options Summary</h2>
  <div class="card">
    <table>
      <tr>
        <td><strong>Total Options P&L</strong></td>
        <td class="${optPnlClass}" style="font-size: 18px; font-weight: bold;">
          ${formatCurrency(optionsSummary.total_options_pnl)} (${formatPercent(optionsSummary.total_options_pnl_percent)})
        </td>
      </tr>
  `;

  if (optionsSummary.best_performing) {
    html += `
      <tr>
        <td>🏆 Best Performer</td>
        <td class="positive">${optionsSummary.best_performing.symbol}: ${formatCurrency(optionsSummary.best_performing.days_gain)}</td>
      </tr>
    `;
  }

  if (optionsSummary.worst_performing) {
    html += `
      <tr>
        <td>📉 Worst Performer</td>
        <td class="negative">${optionsSummary.worst_performing.symbol}: ${formatCurrency(optionsSummary.worst_performing.days_gain)}</td>
      </tr>
    `;
  }

  html += `</table></div>`;
}

// Positions Needing Attention Tomorrow
if (attentionTomorrow.length > 0) {
  html += `
  <h2>⚠️ Needs Attention Tomorrow (${attentionTomorrow.length})</h2>
  <div class="card" style="background: #fff3cd;">
    <table>
      <tr>
        <th>Position</th>
        <th>Days Left</th>
        <th>P&L</th>
        <th>Priority</th>
      </tr>
  `;

  for (const pos of attentionTomorrow) {
    const pnlClass = pos.total_gain >= 0 ? 'positive' : 'negative';
    html += `
      <tr>
        <td><strong>${pos.underlying_symbol}</strong> $${pos.strike_price || ''} ${pos.position_type}</td>
        <td>${pos.days_to_expiration} days</td>
        <td class="${pnlClass}">${formatCurrency(pos.total_gain)}</td>
        <td>${getUrgencyBadge(pos.urgency_level)}</td>
      </tr>
    `;
  }

  html += `
    </table>
    <p style="margin: 10px 0 0 0; font-style: italic;">Review these positions before market open tomorrow.</p>
  </div>
  `;
}

html += `
  <div class="footer">
    <p>This is an automated end-of-day summary. Markets closed at 4:00 PM ET.</p>
  </div>
</body>
</html>
`;

// Build subject line
const totalChange = portfolio.total_portfolio_change_dollars || 0;
const changeEmoji = totalChange >= 0 ? '📈' : '📉';

return [{
  json: {
    subject: `🌆 Market Close - ${changeEmoji} Portfolio ${formatPercent(portfolioVsMarket.portfolio_change_percent)} (${formatCurrency(totalChange)}) | ${portfolioVsMarket.outperformed ? 'Beat' : 'Lagged'} S&P`,
    html: html
  }
}];
```

---

### Node 4: Send Email

Same configuration as Morning workflow.

---

## Workflow Activation & Testing

### Testing Before Activation

1. **Test HTTP endpoint first:**
   ```bash
   curl http://localhost:8080/market-summary?timing=morning
   curl http://localhost:8080/market-summary?timing=close
   ```

2. **Test workflow manually:**
   - Open workflow in n8n
   - Click "Execute Workflow" button
   - Check each node's output

3. **Verify email formatting:**
   - Check the Code node output for valid HTML
   - Send test email to yourself first

### Activating Workflows

1. Open each workflow in n8n
2. Toggle the "Active" switch in the top-right corner
3. Verify both show green "Active" status

### Monitoring Execution

- **Execution History:** Click "Executions" in n8n sidebar
- **Failed Executions:** Filter by "Error" status
- **Logs:** Check n8n console output for detailed errors

---

## Common Workflow Errors & Fixes

### HTTP Request Fails

**Error:** `ECONNREFUSED` or `Connection refused`

**Fix:**
```bash
# Ensure serve.py is running
python serve.py

# Or run it in background
start /B python serve.py
```

**Windows Service Option:**
```powershell
# Create a scheduled task to start serve.py at login
$action = New-ScheduledTaskAction -Execute "pythonw.exe" `
    -Argument "C:\scripts\investment-summary\serve.py"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "Investment API Server" `
    -Action $action -Trigger $trigger
```

---

### JSON Parse Error in Code Node

**Error:** `Cannot read property 'json' of undefined`

**Fix:** Check that HTTP Request node returns valid JSON:
```javascript
// Add error handling at start of Code node
const input = $input.first();
if (!input || !input.json) {
  return [{
    json: {
      subject: "⚠️ Market Summary - Data Unavailable",
      html: "<p>Could not fetch market data. Check serve.py is running.</p>"
    }
  }];
}
const data = input.json;
```

---

### Email Not Sending

**Error:** `Authentication failed` or `Invalid login`

**Fixes:**

1. **Use Gmail App Password** (not regular password):
   - Go to Google Account → Security → 2-Step Verification
   - Scroll to "App passwords" → Generate new password
   - Use this 16-character password in n8n

2. **Check SMTP settings:**
   ```
   Host: smtp.gmail.com
   Port: 587
   Secure: false (use STARTTLS)
   ```

3. **Enable "Less secure apps"** (if not using 2FA):
   - Google Account → Security → Less secure app access → Turn on

---

### Schedule Not Triggering

**Error:** Workflow doesn't run at scheduled time

**Fixes:**

1. **Check timezone:** n8n uses server timezone
   ```bash
   # Check n8n timezone setting
   echo $GENERIC_TIMEZONE
   ```

2. **Verify cron expression:**
   - Use [crontab.guru](https://crontab.guru/) to validate
   - `30 6 * * 1-5` = 6:30 AM Mon-Fri
   - `0 13 * * 1-5` = 1:00 PM Mon-Fri

3. **Check workflow is active:**
   - Toggle switch must be ON (green)

---

### Empty Email Content

**Error:** Email sends but body is empty or malformed

**Fix:** Debug Code node output:
```javascript
// Add at end of Code node before return
console.log('Subject:', subject);
console.log('HTML length:', html.length);
```

Check n8n execution details for console output.

---

## Customization Guide

### Duplicate Workflow for Modifications

1. Open existing workflow
2. Click menu (⋮) → "Duplicate"
3. Rename the duplicate
4. Modify as needed

### Change Email Schedule

Edit the cron expression in Schedule Trigger:

| Schedule | Cron Expression |
|----------|-----------------|
| 7:00 AM Mon-Fri | `0 7 * * 1-5` |
| 8:30 AM Mon-Fri | `30 8 * * 1-5` |
| 4:30 PM Mon-Fri | `30 16 * * 1-5` |
| Every hour 9-5 | `0 9-17 * * 1-5` |
| Every day including weekends | `30 6 * * *` |

### Add SMS Notification

Add a Twilio node after Send Email:
1. **Add Node** → Search "Twilio"
2. Configure with Twilio credentials
3. Set To/From numbers
4. Use `{{ $json.subject }}` as message body

### Add Slack Notification

Add a Slack node:
1. **Add Node** → Search "Slack"
2. Connect Slack workspace
3. Select channel
4. Format message with key metrics

### Modify Email Template

Edit the HTML in the Code node:
- Change colors by modifying hex values
- Add/remove sections by editing HTML structure
- Modify helper functions for different formatting

### Add Additional Data

Modify `daily_market_summary.py` to include new data, then update Code node:
```javascript
// Access new data fields
const newField = data.your_new_field || {};
```

---

## Workflow Export/Import

### Export Workflow

1. Open workflow
2. Click menu (⋮) → "Download"
3. Saves as `.json` file

### Import Workflow

1. Click "Add Workflow" in n8n
2. Select "Import from File"
3. Choose the `.json` file
4. Update credentials (not included in export)

---

## Quick Reference

### Morning Workflow Nodes
```
[Schedule: 30 6 * * 1-5] → [HTTP: ?timing=morning] → [Code: Format] → [Email]
```

### Afternoon Workflow Nodes
```
[Schedule: 0 13 * * 1-5] → [HTTP: ?timing=close] → [Code: Format] → [Email]
```

### Key URLs
```
Morning: http://localhost:8080/market-summary?timing=morning
Close:   http://localhost:8080/market-summary?timing=close
Default: http://localhost:8080/market-summary
```
