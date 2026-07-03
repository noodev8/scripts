#!/usr/bin/env python3
"""
Drill  —  Shopify pricing strategy, Stage 2.

Single-groupid page to decide whether to adjust price. Two blocks:
  * header  — where we are now (price / rrp / cost / stock)
  * pricing — every price we've sold at, in time order, with raw units sold,
              so a stall / acceleration is visible without any maths.

    python shopify-price/drill.py 0129443-ARIZONA
    python shopify-price/drill.py 0129443-ARIZONA --sizes   # add size curve

Size is off by default — it doesn't set the price, it's a guardrail you consult
before a CUT (so you don't misread a sold-out core as dead demand). Shopify only,
positive sales. See STRATEGY.md.
"""

import os
import sys
import argparse
import psycopg2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import get_db_config

ANCHOR = """
    SELECT shopifyprice, NULLIF(cost,'')::numeric AS cost, rrp,
           colour, width, season
    FROM skusummary WHERE groupid = %(g)s
"""

# Every distinct price we've sold at over the window, oldest era first. Raw
# units, no rate — the period is shown so the reader can weigh it themselves.
TIMELINE = """
    SELECT soldprice, SUM(qty) AS units,
           MIN(solddate) AS first_at, MAX(solddate) AS last_at
    FROM sales
    WHERE groupid = %(g)s AND channel = 'SHP' AND qty > 0 AND soldprice > 0
      AND solddate >= CURRENT_DATE - %(days)s
    GROUP BY soldprice
    ORDER BY MIN(solddate)
"""

STOCK_TOTAL = """
    SELECT COALESCE(SUM(qty), 0)
    FROM localstock
    WHERE groupid = %(g)s AND ordernum = '#FREE'
      AND COALESCE(deleted, 0) = 0 AND qty > 0
"""

STOCK_BY_SIZE = """
    SELECT RIGHT(code, 2) AS size, SUM(qty) AS qty
    FROM localstock
    WHERE groupid = %(g)s AND ordernum = '#FREE'
      AND COALESCE(deleted, 0) = 0 AND qty > 0
    GROUP BY RIGHT(code, 2)
    ORDER BY size
"""


def money(x):
    return f"{float(x):.2f}" if x is not None else "-"


def main():
    ap = argparse.ArgumentParser(description="Single-groupid pricing drill-down.")
    ap.add_argument("groupid")
    ap.add_argument("--days", type=int, default=90,
                    help="pricing-history window in days (default 90)")
    ap.add_argument("--sizes", action="store_true",
                    help="also show the remaining-stock size curve")
    args = ap.parse_args()
    g = args.groupid

    conn = psycopg2.connect(**get_db_config())
    try:
        with conn.cursor() as cur:
            cur.execute(ANCHOR, {"g": g})
            a = cur.fetchone()
            if not a:
                sys.exit(f"no skusummary row for {g}")
            price, cost, rrp, colour, width, season = a

            cur.execute(STOCK_TOTAL, {"g": g})
            stock = int(cur.fetchone()[0])

            cur.execute(TIMELINE, {"g": g, "days": args.days})
            timeline = cur.fetchall()

            sizes = None
            if args.sizes:
                cur.execute(STOCK_BY_SIZE, {"g": g})
                sizes = cur.fetchall()
    finally:
        conn.close()

    print()
    print(f"  {g}   {colour or ''} {width or ''}  ({season or '-'})")
    print()

    # Header — vertical table.
    print(f"  {'now':<7}{money(price)}")
    print(f"  {'rrp':<7}{money(rrp)}")
    print(f"  {'cost':<7}{money(cost)}")
    print(f"  {'stock':<7}{stock}")
    print()

    # Pricing — every price sold at, oldest first, raw units.
    print(f"  {'price':<8}{'selling period':<20}{'sold':>5}")
    if not timeline:
        print(f"  (no sales in last {args.days}d)")
    for sp, units, first_at, last_at in timeline:
        end = "now" if float(sp) == float(price) else f"{last_at:%b %d}"
        period = f"{first_at:%b %d} - {end}"
        print(f"  {money(sp):<8}{period:<20}{int(units):>5}")
    print()

    if sizes is not None:
        curve = "  ".join(f"{sz}:{int(q)}" for sz, q in sizes)
        print(f"  sizes  {curve or '(none)'}")
        print()


if __name__ == "__main__":
    main()
