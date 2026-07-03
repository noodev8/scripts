#!/usr/bin/env python3
"""
Latest Sales  —  Shopify pricing strategy, Stage 1.

Sanity triage for a segment: a shortlist of in-stock recent-selling styles to
drill into later. One row per groupid (NOT per sale line), ranked by units sold
in the window (strongest sellers first). Always filtered to one segment.

    python shopify-price/latest_sales.py EVA-SEG
    python shopify-price/latest_sales.py EVA-SEG --days 30 --limit 10

Defaults: segment=EVA-SEG, days=30, limit=10, channel=SHP.

Columns: qty (units sold in window), groupid, stock (current sellable units).
Deliberately minimal — the groupid is the pick; all product detail is derived on
drill-down. Styles with 0 current stock are dropped — nothing to price and (for
Birkenstock) no restock lever; the limit tops the list back up to 10. Size, date,
price and product description are left to drill-down. Returns (qty<0) and £0
lines are excluded. See STRATEGY.md.
"""

import os
import sys
import argparse
import psycopg2

# Import shared DB config from the repo root (same pattern as apply_prices.py)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import get_db_config

# One row per groupid, ranked by units sold in the window (strongest sellers
# first). qty = units sold across the window; tie-break on the style's most
# recent sale so a fresher seller edges an equal-volume staler one.
#
# stock = current sellable warehouse units (localstock, #FREE, not deleted).
# INNER JOIN to the stock CTE drops styles with 0 current stock — nothing to
# price and (for Birkenstock, ~95% of Shopify) no restock lever, so they'd be
# noise; the LIMIT then tops the list back up to 10 in-stock candidates.
# Incoming/allocated stock is deliberately NOT considered here (later stage).
#
# weeks_cover = stock / weekly run-rate = stock * days / (units * 7). At current
# pace, roughly how long until it's gone. Thin cover on a fast seller is the
# harvest signal (price up), not a restock flag. See STRATEGY.md.
QUERY = """
    WITH win AS (
        SELECT s.groupid,
               SUM(s.qty) AS units,
               MAX(s.solddate::text || ' ' || LPAD(COALESCE(s.ordertime,'00:00'), 5, '0')) AS last_ts
        FROM sales s
        JOIN skusummary ss ON ss.groupid = s.groupid
        WHERE ss.segment = %(segment)s
          AND s.channel  = %(channel)s
          AND s.qty > 0 AND s.soldprice > 0
          AND s.solddate >= CURRENT_DATE - %(days)s
          -- Parked-style gate: drop anything with a future review date, so a style
          -- we've just decided on doesn't loop straight back. NULL = never parked.
          AND (ss.nextreviewdate IS NULL OR ss.nextreviewdate <= CURRENT_DATE)
        GROUP BY s.groupid
    ),
    stk AS (
        SELECT groupid, SUM(qty) AS stock
        FROM localstock
        WHERE ordernum = '#FREE' AND COALESCE(deleted,0) = 0 AND qty > 0
        GROUP BY groupid
    )
    SELECT w.groupid, w.units, st.stock
    FROM win w
    JOIN stk st ON st.groupid = w.groupid
    ORDER BY w.units DESC, w.last_ts DESC
    LIMIT %(limit)s
"""


def fetch(segment, days, limit, channel):
    conn = psycopg2.connect(**get_db_config())
    try:
        with conn.cursor() as cur:
            cur.execute(QUERY, {
                "segment": segment, "channel": channel,
                "days": days, "limit": limit,
            })
            return cur.fetchall()
    finally:
        conn.close()


def render(rows, segment, days, channel):
    print()
    width = 4 + 2 + 18 + 7
    print(f"Latest {len(rows)} in-stock selling styles  |  segment {segment}  |  "
          f"{channel}, last {days} days")
    print("=" * width)
    if not rows:
        print("  (no in-stock sales in window)")
        print()
        return
    print(f"{'qty':>4}  {'groupid':<18}{'stock':>7}")
    print("-" * width)
    for groupid, units, stock in rows:
        print(f"{units:>4}  {groupid:<18}{stock:>7}")
    print()


def main():
    ap = argparse.ArgumentParser(description="Latest Shopify sales for a segment.")
    ap.add_argument("segment", nargs="?", default="EVA-SEG",
                    help="skusummary.segment code (default: EVA-SEG)")
    ap.add_argument("--days", type=int, default=30, help="window in days (default 30)")
    ap.add_argument("--limit", type=int, default=10, help="max rows (default 10)")
    ap.add_argument("--channel", default="SHP", help="sales channel (default SHP)")
    args = ap.parse_args()

    rows = fetch(args.segment, args.days, args.limit, args.channel)
    render(rows, args.segment, args.days, args.channel)


if __name__ == "__main__":
    main()
