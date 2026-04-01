#!/usr/bin/env python3
"""
SHOPIFY TRANSACTION REPORT GENERATOR
=====================================

Generates a CSV matching the Shopify Admin "Analytics > Reports > Shopify Transaction"
export format, using the Shopify Orders API.

Output: Shopify Transaction.csv (in script directory)

Usage:
  python shopify_transaction_report.py              # Last month
  python shopify_transaction_report.py 2026-03      # Specific month
"""

import csv
import os
import sys
import time
import requests
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
from collections import defaultdict
from dotenv import load_dotenv
from logging_utils import manage_log_files, create_logger

# --- CONFIGURATION ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

SHOP_DOMAIN = "brookfieldcomfort2.myshopify.com"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN') or os.getenv('SHOPIFY_ORDERS_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("No Shopify access token found in .env (tried SHOPIFY_ACCESS_TOKEN and SHOPIFY_ORDERS_ACCESS_TOKEN)")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_NAME = "shopify_transaction_report"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


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
    start = date(year, month, 1)
    end = date(year, month, last_day)
    return start, end


def fetch_all_orders(start_date, end_date):
    """Fetch orders via REST API with pagination.

    Two passes:
    1. Orders created in the target month (for sale rows)
    2. Older orders updated during the target month (to catch refunds on prior orders)
    """
    # Pass 1: orders created in the target month
    log("--- Pass 1: orders created in target month ---")
    current_month = _fetch_orders_page(
        created_min=f"{start_date}T00:00:00+00:00",
        created_max=f"{end_date}T23:59:59+00:00",
    )

    # Pass 2: older orders that were updated during the target month
    # (these may have refunds that fall within our date range)
    lookback_start = start_date - timedelta(days=90)
    lookback_end = start_date - timedelta(days=1)
    log("--- Pass 2: older orders updated in target month (refund lookback) ---")
    older_orders = _fetch_orders_page(
        created_min=f"{lookback_start}T00:00:00+00:00",
        created_max=f"{lookback_end}T23:59:59+00:00",
        updated_min=f"{start_date}T00:00:00+00:00",
    )

    # Deduplicate by order ID
    seen = {o["id"] for o in current_month}
    for o in older_orders:
        if o["id"] not in seen:
            current_month.append(o)
            seen.add(o["id"])

    log(f"Total unique orders: {len(current_month)}")
    return current_month


def _fetch_orders_page(created_min, created_max, updated_min=None):
    """Fetch paginated orders with the given filters."""
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    all_orders = []

    params = {
        "created_at_min": created_min,
        "created_at_max": created_max,
        "status": "any",
        "limit": 250,
        "fields": "id,name,created_at,taxes_included,line_items,shipping_lines,refunds,discount_applications,tax_lines",
    }
    if updated_min:
        params["updated_at_min"] = updated_min

    url = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/orders.json"
    page = 1

    while url:
        log(f"Fetching orders page {page}...")
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", 2))
            log(f"Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            continue

        if response.status_code != 200:
            log(f"ERROR: Shopify API {response.status_code}: {response.text}")
            break

        orders = response.json().get("orders", [])
        all_orders.extend(orders)
        log(f"  Got {len(orders)} orders (total: {len(all_orders)})")

        # Check for next page via Link header
        link_header = response.headers.get("Link", "")
        url = None
        params = None  # Only use params on first request
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part.split("<")[1].split(">")[0]
                break

        page += 1
        time.sleep(0.25)

    return all_orders


def d(value):
    """Convert to Decimal, default 0."""
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def build_rows(orders, start_date, end_date):
    """
    Build CSV rows matching the Shopify Transaction report format.

    Sale/shipping rows use the order's created_at date and are only included
    if the order was created within the target month.

    Refund rows use the refund's created_at date and are included if the
    refund falls within the target month (even if the order is older).
    """
    rows = []
    start_str = str(start_date)
    end_str = str(end_date)

    for order in orders:
        order_name = order["name"]
        order_date = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        order_in_range = start_str <= order_date <= end_str

        taxes_included = order.get("taxes_included", False)

        # --- Pre-scan refunds for shipping refund amounts ---
        # Shipping refunds offset the original shipping row rather than
        # appearing as separate Returns rows in the Shopify report.
        shipping_refund_total = Decimal("0")
        shipping_refund_tax = Decimal("0")
        for refund in order.get("refunds", []):
            refund_date = datetime.fromisoformat(
                refund["created_at"].replace("Z", "+00:00")
            ).strftime("%Y-%m-%d")
            if not (start_str <= refund_date <= end_str):
                continue
            for adj in refund.get("order_adjustments", []):
                if adj.get("kind") == "shipping_refund":
                    shipping_refund_total += d(adj.get("amount"))
                    shipping_refund_tax += d(adj.get("tax_amount"))

        # --- LINE ITEM ROWS (only for orders created in the target month) ---
        if order_in_range:
            for item in order.get("line_items", []):
                sku = item.get("sku") or ""
                title = item.get("title") or ""
                variant_title = item.get("variant_title") or ""
                if variant_title and variant_title not in title:
                    title = f"{title} {variant_title}"

                qty = int(item.get("quantity", 1))
                unit_price = d(item.get("price"))
                line_total = unit_price * qty

                # Item-level tax
                tax = Decimal("0")
                for tl in item.get("tax_lines", []):
                    tax += d(tl.get("price"))

                # If prices include tax, gross is the tax-exclusive amount
                gross = (line_total - tax) if taxes_included else line_total

                # Item-level discount from discount_allocations
                discount = Decimal("0")
                for alloc in item.get("discount_allocations", []):
                    discount += d(alloc.get("amount"))

                net = gross - discount
                total = net + tax

                rows.append({
                    "Day": order_date,
                    "Order name": order_name,
                    "Product title at time of sale": title,
                    "Product variant SKU": sku,
                    "Gross sales": gross,
                    "Discounts": -discount if discount else Decimal("0"),
                    "Returns": Decimal("0"),
                    "Net sales": net,
                    "Shipping charges": Decimal("0"),
                    "Taxes": tax,
                    "Total sales": total,
                })

            # --- SHIPPING ROW ---
            # Net the original shipping charge against any shipping refunds.
            # When fully refunded, the row is omitted (nets to 0).
            shipping_total = Decimal("0")
            shipping_tax = Decimal("0")
            for sl in order.get("shipping_lines", []):
                sl_price = d(sl.get("price"))
                sl_tax = Decimal("0")
                for tl in sl.get("tax_lines", []):
                    sl_tax += d(tl.get("price"))
                shipping_total += (sl_price - sl_tax) if taxes_included else sl_price
                shipping_tax += sl_tax

            # Apply shipping refunds (amounts are negative, so add them)
            shipping_total += shipping_refund_total
            shipping_tax += shipping_refund_tax

            if shipping_total or shipping_tax:
                rows.append({
                    "Day": order_date,
                    "Order name": order_name,
                    "Product title at time of sale": "",
                    "Product variant SKU": "",
                    "Gross sales": Decimal("0"),
                    "Discounts": Decimal("0"),
                    "Returns": Decimal("0"),
                    "Net sales": Decimal("0"),
                    "Shipping charges": shipping_total,
                    "Taxes": shipping_tax,
                    "Total sales": shipping_total + shipping_tax,
                })

        # --- REFUND / RETURN ROWS (any order, filtered by refund date) ---
        for refund in order.get("refunds", []):
            refund_date = datetime.fromisoformat(
                refund["created_at"].replace("Z", "+00:00")
            ).strftime("%Y-%m-%d")

            if not (start_str <= refund_date <= end_str):
                continue

            for ref_item in refund.get("refund_line_items", []):
                line_item = ref_item.get("line_item", {})
                sku = line_item.get("sku") or ""
                title = line_item.get("title") or ""
                variant_title = line_item.get("variant_title") or ""
                if variant_title and variant_title not in title:
                    title = f"{title} {variant_title}"

                subtotal = d(ref_item.get("subtotal"))
                total_tax = d(ref_item.get("total_tax"))

                # subtotal is tax-inclusive when the order uses inclusive pricing
                refund_excl_tax = (subtotal - total_tax) if taxes_included else subtotal
                returns = -refund_excl_tax
                tax = -total_tax
                net = returns
                total = returns + tax

                rows.append({
                    "Day": refund_date,
                    "Order name": order_name,
                    "Product title at time of sale": title,
                    "Product variant SKU": sku,
                    "Gross sales": Decimal("0"),
                    "Discounts": Decimal("0"),
                    "Returns": returns,
                    "Net sales": net,
                    "Shipping charges": Decimal("0"),
                    "Taxes": tax,
                    "Total sales": total,
                })

            # Non-shipping order adjustments (restocking fees, discrepancies)
            # shown as a single net Returns row. Shipping refunds are handled
            # above by offsetting the original shipping row.
            # The API may include cancelling pairs (e.g. +71.39/-71.39 for
            # "Pending refund discrepancy"), so we net all adjustments.
            adj_total = Decimal("0")
            adj_tax_total = Decimal("0")
            for adj in refund.get("order_adjustments", []):
                if adj.get("kind") == "shipping_refund":
                    continue  # Already handled in shipping row
                adj_total += d(adj.get("amount"))
                adj_tax_total += d(adj.get("tax_amount"))

            net_adj = adj_total + adj_tax_total
            if net_adj:
                rows.append({
                    "Day": refund_date,
                    "Order name": order_name,
                    "Product title at time of sale": "",
                    "Product variant SKU": "",
                    "Gross sales": Decimal("0"),
                    "Discounts": Decimal("0"),
                    "Returns": net_adj,
                    "Net sales": net_adj,
                    "Shipping charges": Decimal("0"),
                    "Taxes": Decimal("0"),
                    "Total sales": net_adj,
                })

    return rows


def format_num(val):
    """Format Decimal for CSV output — match Shopify's format."""
    if val == 0:
        return "0"
    return str(val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def write_csv(rows, start_date, end_date):
    """Write rows to CSV in Shopify Transaction report format."""
    # Sort by date, then order name
    rows.sort(key=lambda r: (r["Day"], r["Order name"]))

    output_path = os.path.join(SCRIPT_DIR, "Shopify Transaction.csv")
    fieldnames = [
        "Day", "Order name", "Product title at time of sale",
        "Product variant SKU", "Gross sales", "Discounts", "Returns",
        "Net sales", "Shipping charges", "Taxes", "Total sales",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                "Day": row["Day"],
                "Order name": row["Order name"],
                "Product title at time of sale": row["Product title at time of sale"],
                "Product variant SKU": row["Product variant SKU"],
                "Gross sales": format_num(row["Gross sales"]),
                "Discounts": format_num(row["Discounts"]),
                "Returns": format_num(row["Returns"]),
                "Net sales": format_num(row["Net sales"]),
                "Shipping charges": format_num(row["Shipping charges"]),
                "Taxes": format_num(row["Taxes"]),
                "Total sales": format_num(row["Total sales"]),
            })

    log(f"Written {len(rows)} rows to {output_path}")
    return output_path


def main():
    month_arg = sys.argv[1] if len(sys.argv) > 1 else None
    start_date, end_date = get_date_range(month_arg)

    log(f"=== SHOPIFY TRANSACTION REPORT ===")
    log(f"Period: {start_date} to {end_date}")

    orders = fetch_all_orders(start_date, end_date)

    if not orders:
        log("No orders found for this period")
        return 0

    rows = build_rows(orders, start_date, end_date)

    output_path = write_csv(rows, start_date, end_date)

    # Summary
    totals = defaultdict(Decimal)
    for r in rows:
        for col in ["Gross sales", "Discounts", "Returns", "Net sales",
                     "Shipping charges", "Taxes", "Total sales"]:
            totals[col] += r[col]

    log(f"--- Summary ---")
    log(f"  Rows:     {len(rows)}")
    log(f"  Gross:    {format_num(totals['Gross sales'])}")
    log(f"  Discounts:{format_num(totals['Discounts'])}")
    log(f"  Returns:  {format_num(totals['Returns'])}")
    log(f"  Net:      {format_num(totals['Net sales'])}")
    log(f"  Shipping: {format_num(totals['Shipping charges'])}")
    log(f"  Tax:      {format_num(totals['Taxes'])}")
    log(f"  Total:    {format_num(totals['Total sales'])}")
    log(f"Output: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
