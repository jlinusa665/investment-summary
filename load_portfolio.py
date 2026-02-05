#!/usr/bin/env python3
"""
Portfolio Loader

Reads portfolio holdings from a CSV file exported from a brokerage account.
Filters out options (Calls/Puts), cash positions, and total rows,
returning only regular stock holdings as a {Symbol: Quantity} dictionary.
"""

import csv
import os

PORTFOLIO_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "private_data", "portfolio.csv")

SKIP_SYMBOLS = {"CASH", "TOTAL"}


def load_portfolio(csv_path=PORTFOLIO_CSV):
    """
    Load portfolio holdings from a brokerage CSV export.

    Args:
        csv_path: Path to the portfolio CSV file.

    Returns:
        Dictionary mapping stock symbol to number of shares (int),
        or None if the file does not exist.
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


if __name__ == "__main__":
    import json
    result = load_portfolio()
    if result is None:
        print(f"No portfolio file found at {PORTFOLIO_CSV}")
    else:
        print(json.dumps(result, indent=2))
