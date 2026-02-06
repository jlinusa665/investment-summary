#!/usr/bin/env python3
"""
Daily Market Summary Script

Fetches S&P 500 and VIX data from Yahoo Finance and outputs
a JSON summary with current prices and daily percentage changes.
"""

import argparse
import json
import sys
from datetime import datetime

from load_portfolio import load_portfolio, load_full_portfolio

# =============================================================================
# Ticker Configuration
# =============================================================================
# Add or remove tickers here to customize the market summary
# Format: (symbol, display_name, key_name)

INDICES = [
    ("^GSPC", "S&P 500", "sp500"),
    ("^VIX", "CBOE Volatility Index", "vix"),
]

STOCKS = [
    ("AAPL", "Apple Inc.", "aapl"),
    ("MSFT", "Microsoft Corporation", "msft"),
    ("GOOGL", "Alphabet Inc.", "googl"),
    ("NVDA", "NVIDIA Corporation", "nvda"),
    ("TSLA", "Tesla Inc.", "tsla"),
]

# =============================================================================
# Portfolio Configuration
# =============================================================================
# Loaded from private_data/portfolio.csv if available, otherwise uses mock data.
# The CSV should have columns: Symbol, Quantity, etc.
# Options (Call/Put), CASH, and TOTAL rows are automatically filtered out.

MOCK_PORTFOLIO = {
    "AAPL": 100,    # 100 shares of Apple
    "MSFT": 50,     # 50 shares of Microsoft
    "GOOGL": 25,    # 25 shares of Alphabet
    "NVDA": 50,     # 50 shares of NVIDIA
    "TSLA": 30,     # 30 shares of Tesla
}

# Load full portfolio (stocks + options) if available
_full_portfolio = load_full_portfolio()
if _full_portfolio:
    PORTFOLIO = _full_portfolio["stocks_portfolio"]
    OPTIONS_PORTFOLIO = _full_portfolio["options_portfolio"]
else:
    PORTFOLIO = MOCK_PORTFOLIO
    OPTIONS_PORTFOLIO = []

# =============================================================================
# Argument Parsing
# =============================================================================
# Set up command-line arguments, including --test flag for sample data mode

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch daily market summary for S&P 500 and VIX"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Return sample data without making API calls"
    )
    parser.add_argument(
        "--timing",
        choices=["morning", "close"],
        default=None,
        help="Timing mode: 'morning' for pre-market preview, 'close' for end-of-day recap"
    )
    return parser.parse_args()


# =============================================================================
# Sample Data for Testing
# =============================================================================
# Returns mock data when --test flag is used, useful for development and testing

def get_sample_data():
    """Return sample market data for testing purposes."""
    return {
        "timestamp": datetime.now().isoformat(),
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
        },
        "stocks": {
            "aapl": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "current_price": 185.92,
                "previous_close": 184.40,
                "daily_change_percent": 0.82
            },
            "msft": {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "current_price": 415.50,
                "previous_close": 411.22,
                "daily_change_percent": 1.04
            },
            "googl": {
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "current_price": 141.80,
                "previous_close": 140.95,
                "daily_change_percent": 0.60
            },
            "nvda": {
                "symbol": "NVDA",
                "name": "NVIDIA Corporation",
                "current_price": 682.35,
                "previous_close": 674.72,
                "daily_change_percent": 1.13
            },
            "tsla": {
                "symbol": "TSLA",
                "name": "Tesla Inc.",
                "current_price": 207.83,
                "previous_close": 211.88,
                "daily_change_percent": -1.91
            }
        },
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
                },
                "msft": {
                    "symbol": "MSFT",
                    "shares": 50,
                    "current_value": 20775.00,
                    "daily_change_dollars": 214.00
                },
                "googl": {
                    "symbol": "GOOGL",
                    "shares": 25,
                    "current_value": 3545.00,
                    "daily_change_dollars": 21.25
                },
                "nvda": {
                    "symbol": "NVDA",
                    "shares": 50,
                    "current_value": 34117.50,
                    "daily_change_dollars": 381.50
                },
                "tsla": {
                    "symbol": "TSLA",
                    "shares": 30,
                    "current_value": 6234.90,
                    "daily_change_dollars": -121.50
                }
            }
        },
        "options": {
            "total_options_value": 5250.00,
            "total_options_change_dollars": 125.50,
            "total_options_change_percent": 2.45,
            "options_positions": [
                {
                    "symbol": "AAPL250207C00190000",
                    "underlying_symbol": "AAPL",
                    "position_type": "Call",
                    "is_short": True,
                    "days_to_expiration": 0,
                    "expiration_date": "2025-02-07",
                    "current_value": -850.00,
                    "days_gain": 75.00,
                    "total_gain": 425.00,
                    "total_gain_percent": 33.3
                },
                {
                    "symbol": "MSFT250214P00400000",
                    "underlying_symbol": "MSFT",
                    "position_type": "Put",
                    "is_short": False,
                    "days_to_expiration": 1,
                    "expiration_date": "2025-02-14",
                    "current_value": 1200.00,
                    "days_gain": -150.00,
                    "total_gain": -300.00,
                    "total_gain_percent": -20.0
                },
                {
                    "symbol": "NVDA250221C00700000",
                    "underlying_symbol": "NVDA",
                    "position_type": "Call",
                    "is_short": True,
                    "days_to_expiration": 7,
                    "expiration_date": "2025-02-21",
                    "current_value": -2100.00,
                    "days_gain": 200.50,
                    "total_gain": 1850.00,
                    "total_gain_percent": 46.8
                }
            ]
        },
        "action_recommendations": {
            "profit_taking_opportunities": [],
            "urgent_losses": [
                {
                    "symbol": "MSFT250214P00400000",
                    "underlying_symbol": "MSFT",
                    "days_to_expiration": 1,
                    "expiration_date": "2025-02-14",
                    "current_value": 1200.00,
                    "total_gain": -300.00,
                    "total_gain_percent": -20.0,
                    "position_type": "Put",
                    "is_short": False,
                    "combined_priority_score": 85.0,
                    "urgency_level": "HIGH",
                    "recommended_action": "HIGH PRIORITY - Consider closing to stop losses"
                }
            ],
            "expiring_this_week": [
                {
                    "symbol": "AAPL250207C00190000",
                    "underlying_symbol": "AAPL",
                    "days_to_expiration": 0,
                    "expiration_date": "2025-02-07",
                    "current_value": -850.00,
                    "total_gain": 425.00,
                    "total_gain_percent": 33.3,
                    "position_type": "Call",
                    "is_short": True,
                    "combined_priority_score": 40.0,
                    "urgency_level": "LOW",
                    "recommended_action": "HOLD - Position is profitable, no immediate action needed"
                },
                {
                    "symbol": "MSFT250214P00400000",
                    "underlying_symbol": "MSFT",
                    "days_to_expiration": 1,
                    "expiration_date": "2025-02-14",
                    "current_value": 1200.00,
                    "total_gain": -300.00,
                    "total_gain_percent": -20.0,
                    "position_type": "Put",
                    "is_short": False,
                    "combined_priority_score": 85.0,
                    "urgency_level": "HIGH",
                    "recommended_action": "HIGH PRIORITY - Consider closing to stop losses"
                }
            ],
            "expiring_next_week": [],
            "all_positions_by_priority": [
                {
                    "symbol": "MSFT250214P00400000",
                    "underlying_symbol": "MSFT",
                    "days_to_expiration": 1,
                    "expiration_date": "2025-02-14",
                    "current_value": 1200.00,
                    "total_gain": -300.00,
                    "total_gain_percent": -20.0,
                    "position_type": "Put",
                    "is_short": False,
                    "combined_priority_score": 85.0,
                    "urgency_level": "HIGH",
                    "recommended_action": "HIGH PRIORITY - Consider closing to stop losses"
                },
                {
                    "symbol": "NVDA250221C00700000",
                    "underlying_symbol": "NVDA",
                    "days_to_expiration": 7,
                    "expiration_date": "2025-02-21",
                    "current_value": -2100.00,
                    "total_gain": 1850.00,
                    "total_gain_percent": 46.8,
                    "position_type": "Call",
                    "is_short": True,
                    "combined_priority_score": 40.0,
                    "urgency_level": "LOW",
                    "recommended_action": "HOLD - Position is profitable, no immediate action needed"
                },
                {
                    "symbol": "AAPL250207C00190000",
                    "underlying_symbol": "AAPL",
                    "days_to_expiration": 0,
                    "expiration_date": "2025-02-07",
                    "current_value": -850.00,
                    "total_gain": 425.00,
                    "total_gain_percent": 33.3,
                    "position_type": "Call",
                    "is_short": True,
                    "combined_priority_score": 40.0,
                    "urgency_level": "LOW",
                    "recommended_action": "HOLD - Position is profitable, no immediate action needed"
                }
            ]
        },
        "status": "success",
        "mode": "test"
    }


# =============================================================================
# Market Data Fetching
# =============================================================================
# Uses yfinance library to fetch real-time data from Yahoo Finance API
# yfinance uses dashes instead of dots for share classes (e.g., BRK-B not BRK.B)
YFINANCE_SYMBOL_MAP = {
    "BRK.B": "BRK-B",
    "BRK.A": "BRK-A",
}

def fetch_ticker_data(symbol, name):
    """
    Fetch current price and calculate daily percentage change for a ticker.

    Args:
        symbol: The ticker symbol (e.g., "^GSPC")
        name: Human-readable name for the ticker

    Returns:
        Dictionary with price data and daily change, or None if fetch fails
    """
    import yfinance as yf

    try:
        # Create ticker object and fetch data
        yf_symbol = YFINANCE_SYMBOL_MAP.get(symbol, symbol)
        ticker = yf.Ticker(yf_symbol)

        # Get current market data
        info = ticker.info

        # Extract current price - try multiple fields as availability varies
        current_price = info.get("regularMarketPrice") or info.get("currentPrice")
        previous_close = info.get("regularMarketPreviousClose") or info.get("previousClose")

        # Validate we got the required data
        if current_price is None or previous_close is None:
            raise ValueError(f"Could not retrieve price data for {symbol}")

        # Calculate daily percentage change
        daily_change_percent = ((current_price - previous_close) / previous_close) * 100

        return {
            "symbol": symbol,
            "name": name,
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "daily_change_percent": round(daily_change_percent, 2)
        }

    except Exception as e:
        # Return error information for this specific ticker
        return {
            "symbol": symbol,
            "name": name,
            "error": str(e)
        }


def fetch_market_data():
    """
    Fetch market data for indices and stocks defined in INDICES and STOCKS lists.

    Returns:
        Dictionary containing market data and status information
    """
    indices_data = {}
    stocks_data = {}
    errors = []

    # Fetch data for each index
    for symbol, name, key in INDICES:
        data = fetch_ticker_data(symbol, name)
        indices_data[key] = data

        # Track any errors that occurred
        if "error" in data:
            errors.append(f"{name}: {data['error']}")

    # Fetch data for each stock
    for symbol, name, key in STOCKS:
        data = fetch_ticker_data(symbol, name)
        stocks_data[key] = data

        # Track any errors that occurred
        if "error" in data:
            errors.append(f"{name}: {data['error']}")

    # Build the response object
    result = {
        "timestamp": datetime.now().isoformat(),
        "indices": indices_data,
        "stocks": stocks_data,
        "status": "success" if not errors else "partial_failure",
        "mode": "live"
    }

    # Include error details if any occurred
    if errors:
        result["errors"] = errors

    # Fetch data for portfolio stocks not already in STOCKS list
    tracked_symbols = {s[0] for s in STOCKS}
    for symbol in PORTFOLIO:
        if symbol not in tracked_symbols:
            key = symbol.lower()
            data = fetch_ticker_data(symbol, symbol)
            stocks_data[key] = data
            if "error" in data:
                errors.append(f"{symbol}: {data['error']}")

    # Calculate portfolio summary if holdings exist
    if PORTFOLIO:
        result["portfolio"] = calculate_portfolio_summary(stocks_data)

    # Calculate options summary if options exist
    if OPTIONS_PORTFOLIO:
        result["options"] = calculate_options_summary(OPTIONS_PORTFOLIO)
        result["action_recommendations"] = calculate_action_recommendations(OPTIONS_PORTFOLIO)

    return result


# =============================================================================
# Portfolio Calculations
# =============================================================================
# Calculates total portfolio value and daily changes based on PORTFOLIO holdings

def calculate_portfolio_summary(stocks_data):
    """
    Calculate portfolio totals based on current stock prices and holdings.

    Args:
        stocks_data: Dictionary of stock data with current and previous prices

    Returns:
        Dictionary with portfolio value, daily change dollars, and daily change percent
    """
    total_current_value = 0.0
    total_previous_value = 0.0
    holdings_detail = {}

    for symbol, shares in PORTFOLIO.items():
        # Find the stock data by matching symbol
        stock_key = symbol.lower()
        stock_data = stocks_data.get(stock_key)

        if stock_data and "error" not in stock_data:
            current_price = stock_data["current_price"]
            previous_close = stock_data["previous_close"]

            # Calculate position values
            current_value = shares * current_price
            previous_value = shares * previous_close

            total_current_value += current_value
            total_previous_value += previous_value

            # Store individual holding details
            holdings_detail[stock_key] = {
                "symbol": symbol,
                "shares": shares,
                "current_value": round(current_value, 2),
                "daily_change_dollars": round(current_value - previous_value, 2)
            }

    # Calculate overall portfolio change
    daily_change_dollars = total_current_value - total_previous_value
    daily_change_percent = 0.0
    if total_previous_value > 0:
        daily_change_percent = (daily_change_dollars / total_previous_value) * 100

    return {
        "total_portfolio_value": round(total_current_value, 2),
        "total_portfolio_change_dollars": round(daily_change_dollars, 2),
        "total_portfolio_change_percent": round(daily_change_percent, 2),
        "per_stock_holdings": holdings_detail
    }


# =============================================================================
# Options Calculations
# =============================================================================
# Calculates options summary including totals, expiring soon, and position summaries

def calculate_options_summary(options_portfolio):
    """
    Calculate options portfolio summary.

    Args:
        options_portfolio: List of option position dictionaries

    Returns:
        Dictionary with options totals, positions, expiring soon, and summaries
    """
    if not options_portfolio:
        return None

    total_value = 0.0
    total_days_gain = 0.0
    expiring_soon = []
    long_count = 0
    long_value = 0.0
    short_count = 0
    short_value = 0.0

    for opt in options_portfolio:
        value = opt.get("current_value", 0.0)
        days_gain = opt.get("days_gain", 0.0)
        days_to_exp = opt.get("days_to_expiration", 999)
        is_short = opt.get("is_short", False)

        total_value += value
        total_days_gain += days_gain

        # Track expiring soon (< 7 days)
        if days_to_exp < 7:
            expiring_soon.append(opt)

        # Track long vs short positions
        if is_short:
            short_count += 1
            short_value += value
        else:
            long_count += 1
            long_value += value

    # Calculate percentage change (based on previous value)
    previous_value = total_value - total_days_gain
    change_percent = 0.0
    if previous_value != 0:
        change_percent = (total_days_gain / abs(previous_value)) * 100

    return {
        "total_options_value": round(total_value, 2),
        "total_options_change_dollars": round(total_days_gain, 2),
        "total_options_change_percent": round(change_percent, 2),
        "options_positions": options_portfolio,
        "expiring_soon": expiring_soon,
        "long_positions_summary": {
            "count": long_count,
            "total_value": round(long_value, 2)
        },
        "short_positions_summary": {
            "count": short_count,
            "total_value": round(short_value, 2)
        }
    }


# =============================================================================
# Action Recommendations
# =============================================================================
# Analyzes options positions and generates prioritized action recommendations

def calculate_time_urgency_score(days_to_expiration):
    """Calculate time urgency score (0-100) based on days to expiration."""
    if days_to_expiration < 7:
        return 100
    elif days_to_expiration <= 14:
        return 80
    elif days_to_expiration <= 30:
        return 60
    elif days_to_expiration <= 60:
        return 40
    else:
        # Scale down from 40 to 0 for 60-180 days, then 0 beyond
        if days_to_expiration >= 180:
            return 0
        return max(0, 40 - ((days_to_expiration - 60) * 40 / 120))


def calculate_action_recommendations(options_portfolio):
    """
    Generate action recommendations for options positions.

    Args:
        options_portfolio: List of option position dictionaries

    Returns:
        Dictionary with categorized recommendations and scored positions
    """
    if not options_portfolio:
        return None

    # Find the largest absolute loss for scaling
    max_loss_dollars = 0.0
    for opt in options_portfolio:
        total_gain = opt.get("total_gain", 0.0)
        if total_gain < 0:
            max_loss_dollars = max(max_loss_dollars, abs(total_gain))

    # Process each position and calculate scores
    scored_positions = []

    for opt in options_portfolio:
        days_to_exp = opt.get("days_to_expiration", 999)
        total_gain = opt.get("total_gain", 0.0)
        total_gain_percent = opt.get("total_gain_percent", 0.0)
        is_short = opt.get("is_short", False)
        current_value = opt.get("current_value", 0.0)

        # Calculate time urgency score
        time_score = calculate_time_urgency_score(days_to_exp)

        # Calculate loss dollar score (0-100, only for losing positions)
        loss_dollar_score = 0.0
        if total_gain < 0 and max_loss_dollars > 0:
            loss_dollar_score = (abs(total_gain) / max_loss_dollars) * 100

        # Calculate loss percent score (0-100)
        loss_percent_score = 0.0
        if total_gain_percent < 0:
            # Scale from 0 at 0% loss to 100 at -100% loss (or worse)
            loss_percent_score = min(100, abs(total_gain_percent))

        # Combined score: time * 0.4 + loss_dollar * 0.3 + loss_percent * 0.3
        combined_score = (time_score * 0.4) + (loss_dollar_score * 0.3) + (loss_percent_score * 0.3)

        # Determine urgency level
        if combined_score >= 90:
            urgency_level = "CRITICAL"
        elif combined_score >= 70:
            urgency_level = "HIGH"
        elif combined_score >= 50:
            urgency_level = "MEDIUM"
        else:
            urgency_level = "LOW"

        # Determine recommended action
        recommended_action = ""
        if is_short and total_gain_percent >= 60:
            recommended_action = f"BUY TO CLOSE - Lock in {total_gain_percent:.1f}% profit (TAKE PROFIT NOW)"
        elif is_short and total_gain_percent >= 50:
            recommended_action = f"BUY TO CLOSE - Lock in {total_gain_percent:.1f}% profit (CONSIDER CLOSING)"
        elif total_gain < 0:
            if combined_score >= 90:
                recommended_action = "CLOSE IMMEDIATELY - Catastrophic loss, time running out"
            elif combined_score >= 70:
                recommended_action = "HIGH PRIORITY - Consider closing to stop losses"
            elif combined_score >= 50:
                recommended_action = "MONITOR - Review position, consider action if worsens"
            else:
                recommended_action = "WATCH - Track position for changes"
        else:
            recommended_action = "HOLD - Position is profitable, no immediate action needed"

        position_data = {
            "symbol": opt.get("symbol"),
            "underlying_symbol": opt.get("underlying_symbol"),
            "days_to_expiration": days_to_exp,
            "expiration_date": opt.get("expiration_date"),
            "current_value": current_value,
            "total_gain": total_gain,
            "total_gain_percent": total_gain_percent,
            "position_type": opt.get("position_type"),
            "is_short": is_short,
            "time_urgency_score": round(time_score, 2),
            "loss_dollar_score": round(loss_dollar_score, 2),
            "loss_percent_score": round(loss_percent_score, 2),
            "combined_priority_score": round(combined_score, 2),
            "urgency_level": urgency_level,
            "recommended_action": recommended_action,
            "cost_to_close": round(abs(current_value), 2)
        }
        scored_positions.append(position_data)

    # Categorize positions
    profit_taking_opportunities = [
        p for p in scored_positions
        if p["is_short"] and p["total_gain_percent"] >= 50
    ]
    profit_taking_opportunities.sort(key=lambda x: x["total_gain_percent"], reverse=True)

    urgent_losses = [
        p for p in scored_positions
        if p["combined_priority_score"] >= 70 or (p["days_to_expiration"] < 7 and p["total_gain"] < 0)
    ]
    urgent_losses.sort(key=lambda x: x["combined_priority_score"], reverse=True)

    expiring_this_week = [
        p for p in scored_positions
        if p["days_to_expiration"] <= 7
    ]
    expiring_this_week.sort(key=lambda x: x["days_to_expiration"])

    expiring_next_week = [
        p for p in scored_positions
        if p["days_to_expiration"] <= 14
    ]
    expiring_next_week.sort(key=lambda x: x["days_to_expiration"])

    all_by_priority = sorted(scored_positions, key=lambda x: x["combined_priority_score"], reverse=True)

    return {
        "profit_taking_opportunities": profit_taking_opportunities,
        "urgent_losses": urgent_losses,
        "expiring_this_week": expiring_this_week,
        "expiring_next_week": expiring_next_week,
        "all_positions_by_priority": all_by_priority
    }


# =============================================================================
# Timing Mode Functions
# =============================================================================
# Generate morning preview or market close recap based on timing mode

def fetch_premarket_futures():
    """
    Fetch pre-market S&P 500 futures data.

    Returns:
        Dictionary with futures current price, previous close, and trend
    """
    import yfinance as yf

    try:
        # ES=F is the S&P 500 E-mini futures symbol
        ticker = yf.Ticker("ES=F")
        info = ticker.info

        current_price = info.get("regularMarketPrice") or info.get("currentPrice")
        previous_close = info.get("regularMarketPreviousClose") or info.get("previousClose")

        if current_price is None or previous_close is None:
            return {"error": "Could not retrieve futures data"}

        change = current_price - previous_close
        change_percent = (change / previous_close) * 100

        if change_percent > 0.3:
            trend = "bullish"
        elif change_percent < -0.3:
            trend = "bearish"
        else:
            trend = "neutral"

        return {
            "symbol": "ES=F",
            "name": "S&P 500 E-mini Futures",
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "trend": trend
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_premarket_vix():
    """
    Fetch pre-market VIX level.

    Returns:
        Dictionary with VIX current level and interpretation
    """
    import yfinance as yf

    try:
        ticker = yf.Ticker("^VIX")
        info = ticker.info

        current_price = info.get("regularMarketPrice") or info.get("currentPrice")
        previous_close = info.get("regularMarketPreviousClose") or info.get("previousClose")

        if current_price is None:
            return {"error": "Could not retrieve VIX data"}

        # VIX interpretation
        if current_price < 15:
            interpretation = "low_volatility"
        elif current_price < 20:
            interpretation = "normal"
        elif current_price < 30:
            interpretation = "elevated"
        else:
            interpretation = "high_volatility"

        result = {
            "symbol": "^VIX",
            "name": "CBOE Volatility Index",
            "current_level": round(current_price, 2),
            "interpretation": interpretation
        }

        if previous_close:
            result["previous_close"] = round(previous_close, 2)
            result["change"] = round(current_price - previous_close, 2)

        return result
    except Exception as e:
        return {"error": str(e)}


def generate_morning_preview(market_data):
    """
    Generate morning market preview section.

    Args:
        market_data: The base market data dictionary

    Returns:
        Dictionary with market preview information
    """
    preview = {}

    # Pre-market S&P 500 futures
    preview["sp500_futures"] = fetch_premarket_futures()

    # Pre-market VIX level
    preview["vix_premarket"] = fetch_premarket_vix()

    # Today's expirations (days_to_expiration == 0)
    todays_expirations = []
    if "action_recommendations" in market_data and market_data["action_recommendations"]:
        expiring_this_week = market_data["action_recommendations"].get("expiring_this_week", [])
        todays_expirations = [
            pos for pos in expiring_this_week
            if pos.get("days_to_expiration", 999) == 0
        ]
    preview["todays_expirations"] = todays_expirations
    preview["todays_expirations_count"] = len(todays_expirations)

    # Key positions to watch (high priority or expiring soon)
    key_positions = []
    if "action_recommendations" in market_data and market_data["action_recommendations"]:
        all_positions = market_data["action_recommendations"].get("all_positions_by_priority", [])
        # Top 5 positions by priority score
        key_positions = all_positions[:5]
    preview["key_positions_to_watch"] = key_positions

    return preview


def generate_market_close_recap(market_data):
    """
    Generate end-of-day market recap section.

    Args:
        market_data: The base market data dictionary

    Returns:
        Dictionary with market recap information
    """
    recap = {}

    # Final market performance summary
    sp500_data = market_data.get("indices", {}).get("sp500", {})
    vix_data = market_data.get("indices", {}).get("vix", {})

    recap["market_performance"] = {
        "sp500": {
            "close": sp500_data.get("current_price"),
            "change_percent": sp500_data.get("daily_change_percent"),
            "direction": "up" if sp500_data.get("daily_change_percent", 0) >= 0 else "down"
        },
        "vix": {
            "close": vix_data.get("current_price"),
            "change_percent": vix_data.get("daily_change_percent")
        }
    }

    # Portfolio performance vs S&P 500
    portfolio_data = market_data.get("portfolio", {})
    portfolio_change = portfolio_data.get("total_portfolio_change_percent", 0)
    sp500_change = sp500_data.get("daily_change_percent", 0)

    recap["portfolio_vs_market"] = {
        "portfolio_change_percent": portfolio_change,
        "sp500_change_percent": sp500_change,
        "relative_performance": round(portfolio_change - sp500_change, 2),
        "outperformed": portfolio_change > sp500_change
    }

    # Top 3 gainers and losers by dollar amount
    holdings = portfolio_data.get("per_stock_holdings", {})
    holdings_list = list(holdings.values())

    # Sort by daily change dollars
    sorted_by_change = sorted(
        holdings_list,
        key=lambda x: x.get("daily_change_dollars", 0),
        reverse=True
    )

    gainers = [h for h in sorted_by_change if h.get("daily_change_dollars", 0) > 0][:3]
    losers = [h for h in sorted_by_change if h.get("daily_change_dollars", 0) < 0][-3:]
    losers.reverse()  # Most negative first

    recap["top_gainers"] = gainers
    recap["top_losers"] = losers

    # Options summary
    options_data = market_data.get("options", {})
    if options_data:
        options_positions = options_data.get("options_positions", [])

        # Find best and worst performing options by days_gain
        best_option = None
        worst_option = None

        if options_positions:
            sorted_by_gain = sorted(
                options_positions,
                key=lambda x: x.get("days_gain", 0),
                reverse=True
            )
            best_option = sorted_by_gain[0] if sorted_by_gain else None
            worst_option = sorted_by_gain[-1] if sorted_by_gain else None

        recap["options_summary"] = {
            "total_options_pnl": options_data.get("total_options_change_dollars", 0),
            "total_options_pnl_percent": options_data.get("total_options_change_percent", 0),
            "best_performing": {
                "symbol": best_option.get("symbol") if best_option else None,
                "days_gain": best_option.get("days_gain") if best_option else None
            } if best_option else None,
            "worst_performing": {
                "symbol": worst_option.get("symbol") if worst_option else None,
                "days_gain": worst_option.get("days_gain") if worst_option else None
            } if worst_option else None
        }
    else:
        recap["options_summary"] = None

    # Positions needing attention tomorrow
    attention_tomorrow = []
    if "action_recommendations" in market_data and market_data["action_recommendations"]:
        # Positions expiring in 1 day or with high priority
        all_positions = market_data["action_recommendations"].get("all_positions_by_priority", [])
        for pos in all_positions:
            days_to_exp = pos.get("days_to_expiration", 999)
            priority = pos.get("combined_priority_score", 0)
            # Expiring tomorrow or high urgency
            if days_to_exp == 1 or priority >= 70:
                attention_tomorrow.append(pos)
    recap["positions_needing_attention_tomorrow"] = attention_tomorrow

    return recap


# =============================================================================
# Main Entry Point
# =============================================================================
# Orchestrates the script execution and handles output formatting

def main():
    """Main entry point for the script."""
    args = parse_arguments()

    try:
        # Use sample data if --test flag is provided, otherwise fetch live data
        if args.test:
            data = get_sample_data()
        else:
            data = fetch_market_data()

        # Add timing-specific sections if --timing flag is provided
        if args.timing == "morning":
            data["summary_type"] = "morning_preview"
            data["market_preview"] = generate_morning_preview(data)
        elif args.timing == "close":
            data["summary_type"] = "market_close"
            data["market_recap"] = generate_market_close_recap(data)

        # Output results as formatted JSON to stdout
        print(json.dumps(data, indent=2))

        # Exit with appropriate code based on status
        if data["status"] == "success":
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        # Handle any unexpected errors
        error_response = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }
        print(json.dumps(error_response, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
