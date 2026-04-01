#!/usr/bin/env python3
"""
SHOPIFY MONTHLY FEES REPORT
============================

Totals up Shopify Payments fees for a given month using the
Balance Transactions API.

Output: Prints fees total to console.

Usage:
  python shopify_fees.py              # Last month
  python shopify_fees.py 2026-03      # Specific month

Requires: read_shopify_payments_payouts scope on SHOPIFY_ACCESS_TOKEN
"""

import os
import sys
import time
import requests
from datetime import date, timedelta
from decimal import Decimal
from calendar import monthrange
from collections import Counter
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

SHOP_DOMAIN = "brookfieldcomfort2.myshopify.com"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in .env file")


def get_date_range(month_arg=None):
    """Return (first_day, last_day) for the target month. Defaults to last month."""
    if month_arg:
        year, month = map(int, month_arg.split('-'))
    else:
        today = date.today()
        first_of_this_month = today.replace(day=1)
        last_month_last_day = first_of_this_month - timedelta(days=1)
        year, month = last_month_last_day.year, last_month_last_day.month

    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def fetch_transactions(start_date, end_date):
    """Fetch all balance transactions, paginating until we pass the start date."""
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    url = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/shopify_payments/balance/transactions.json"
    params = {"limit": 250}

    all_txns = []
    start_str = str(start_date)
    end_str = str(end_date)
    page = 1

    while url:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", 2))
            time.sleep(retry_after)
            continue

        if response.status_code != 200:
            print(f"ERROR: Shopify API {response.status_code}: {response.text[:200]}")
            break

        txns = response.json().get("transactions", [])
        if not txns:
            break

        # Filter to target month and relevant types
        for t in txns:
            txn_date = t["processed_at"][:10]
            if start_str <= txn_date <= end_str and t["type"] in ("charge", "refund", "dispute"):
                all_txns.append(t)

        # Stop paginating once we've gone past the start of the month
        earliest = min(t["processed_at"][:10] for t in txns)
        if earliest < start_str:
            break

        # Next page
        link_header = response.headers.get("Link", "")
        url = None
        params = None
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part.split("<")[1].split(">")[0]
                break

        page += 1
        time.sleep(0.25)

    return all_txns


def main():
    month_arg = sys.argv[1] if len(sys.argv) > 1 else None
    start_date, end_date = get_date_range(month_arg)
    month_label = start_date.strftime("%B %Y")

    txns = fetch_transactions(start_date, end_date)

    if not txns:
        print(f"{month_label}: No transactions found")
        return 0

    total_fee = sum(Decimal(t["fee"]) for t in txns)
    types = Counter(t["type"] for t in txns)

    breakdown = ", ".join(f"{count} {typ}{'s' if count != 1 else ''}" for typ, count in types.most_common())
    print(f"{month_label} Shopify Fees: £{total_fee} ({breakdown})")

    return 0


if __name__ == "__main__":
    exit(main())
