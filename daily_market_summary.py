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

from load_portfolio import load_portfolio

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

PORTFOLIO = load_portfolio() or MOCK_PORTFOLIO

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
