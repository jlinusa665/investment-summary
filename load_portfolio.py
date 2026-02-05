#!/usr/bin/env python3
"""
Portfolio Loader

Reads portfolio holdings from a CSV file exported from a brokerage account.
Parses both regular stock holdings and options contracts.
Returns separate dictionaries for stocks and options.
"""

import csv
import os
import re
from datetime import datetime, date

PORTFOLIO_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "private_data", "portfolio.csv")

SKIP_SYMBOLS = {"CASH", "TOTAL"}

# Pattern to parse options: "NVDA Feb 27 '26 $195 Call" or "MSFT Dec 17 '27 $410 Call"
# Groups: underlying, month, day, year, strike, option_type
OPTIONS_PATTERN = re.compile(
    r"^([A-Z]+)\s+"           # underlying symbol
    r"([A-Za-z]{3})\s+"       # month (Jan, Feb, etc.)
    r"(\d{1,2})\s+"           # day
    r"'(\d{2})\s+"            # year (2-digit with apostrophe)
    r"\$([0-9.]+)\s+"         # strike price
    r"(Call|Put)$",           # option type
    re.IGNORECASE
)

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


def parse_float(value, default=0.0):
    """Parse a float from a string, handling commas and empty values."""
    if not value:
        return default
    try:
        return float(value.replace(",", "").replace("$", "").replace("%", ""))
    except (ValueError, TypeError):
        return default


def parse_int(value, default=0):
    """Parse an int from a string, handling commas and empty values."""
    if not value:
        return default
    try:
        return int(float(value.replace(",", "")))
    except (ValueError, TypeError):
        return default


def parse_option_symbol(symbol):
    """
    Parse an option symbol into its components.

    Args:
        symbol: Option symbol like "NVDA Feb 27 '26 $195 Call"

    Returns:
        Dictionary with parsed components, or None if not an option.
    """
    match = OPTIONS_PATTERN.match(symbol.strip())
    if not match:
        return None

    underlying, month_str, day, year_2digit, strike, option_type = match.groups()

    # Parse expiration date
    month = MONTH_MAP.get(month_str.lower())
    if not month:
        return None

    # Convert 2-digit year to 4-digit (assume 2000s)
    year = 2000 + int(year_2digit)

    try:
        expiration_date = date(year, month, int(day))
    except ValueError:
        return None

    # Calculate days to expiration
    today = date.today()
    days_to_expiration = (expiration_date - today).days

    return {
        "underlying_symbol": underlying.upper(),
        "expiration_date": expiration_date.isoformat(),
        "strike_price": float(strike),
        "option_type": option_type.capitalize(),
        "days_to_expiration": days_to_expiration
    }


def load_portfolio(csv_path=PORTFOLIO_CSV):
    """
    Load portfolio holdings from a brokerage CSV export.

    Args:
        csv_path: Path to the portfolio CSV file.

    Returns:
        Dictionary mapping stock symbol to number of shares (int),
        or None if the file does not exist.

    Note: For full portfolio data including options, use load_full_portfolio().
    """
    if not os.path.exists(csv_path):
        return None

    portfolio = {}

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            symbol = row.get("Symbol", "").strip()

            if not symbol:
                continue

            # Skip options contracts
            if "Call" in symbol or "Put" in symbol:
                continue

            # Skip cash and total rows
            if symbol.upper() in SKIP_SYMBOLS:
                continue

            # Parse quantity, stripping commas and converting to int
            try:
                quantity = int(float(row.get("Quantity", "0").replace(",", "")))
            except (ValueError, TypeError):
                continue

            if quantity > 0:
                portfolio[symbol.upper()] = quantity

    return portfolio


def load_full_portfolio(csv_path=PORTFOLIO_CSV):
    """
    Load full portfolio including stocks and options from a brokerage CSV export.

    Args:
        csv_path: Path to the portfolio CSV file.

    Returns:
        Dictionary with:
            - stocks_portfolio: {symbol: quantity} for regular stocks
            - options_portfolio: list of option position dictionaries
        Or None if the file does not exist.
    """
    if not os.path.exists(csv_path):
        return None

    stocks_portfolio = {}
    options_portfolio = []

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            symbol = row.get("Symbol", "").strip()

            if not symbol:
                continue

            # Skip cash and total rows
            if symbol.upper() in SKIP_SYMBOLS:
                continue

            # Check if it's an option
            option_info = parse_option_symbol(symbol)

            if option_info:
                # Parse option position data
                quantity = parse_int(row.get("Quantity", "0"))

                option_position = {
                    "symbol": symbol,
                    "underlying_symbol": option_info["underlying_symbol"],
                    "expiration_date": option_info["expiration_date"],
                    "strike_price": option_info["strike_price"],
                    "option_type": option_info["option_type"],
                    "days_to_expiration": option_info["days_to_expiration"],
                    "quantity": quantity,
                    "is_short": quantity < 0,
                    "position_type": "short" if quantity < 0 else "long",
                    "price_paid": parse_float(row.get("Price Paid $")),
                    "current_price": parse_float(row.get("Last Price $")),
                    "days_gain": parse_float(row.get("Day's Gain $")),
                    "total_gain": parse_float(row.get("Total Gain $")),
                    "total_gain_percent": parse_float(row.get("Total Gain %")),
                    "current_value": parse_float(row.get("Value $"))
                }
                options_portfolio.append(option_position)
            else:
                # Regular stock
                quantity = parse_int(row.get("Quantity", "0"))

                if quantity > 0:
                    stocks_portfolio[symbol.upper()] = quantity

    return {
        "stocks_portfolio": stocks_portfolio,
        "options_portfolio": options_portfolio
    }


if __name__ == "__main__":
    import json

    print("=== Stocks Only (load_portfolio) ===")
    stocks = load_portfolio()
    if stocks is None:
        print(f"No portfolio file found at {PORTFOLIO_CSV}")
    else:
        print(json.dumps(stocks, indent=2))

    print("\n=== Full Portfolio (load_full_portfolio) ===")
    full = load_full_portfolio()
    if full is None:
        print(f"No portfolio file found at {PORTFOLIO_CSV}")
    else:
        print(f"Stocks: {len(full['stocks_portfolio'])} positions")
        print(json.dumps(full['stocks_portfolio'], indent=2))
        print(f"\nOptions: {len(full['options_portfolio'])} positions")
        for opt in full['options_portfolio']:
            print(json.dumps(opt, indent=2))
