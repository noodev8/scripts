#!/usr/bin/env python3
"""
Review  —  Shopify pricing strategy: park a groupid.

Sets skusummary.next_shopify_price_review to today + <days>, so the style drops out of the
Stage 1 triage (latest_sales.py) until that date passes.

    python shopify-price/review.py 0129443-ARIZONA 7

Use it after a "no change" decision, or any time you want to stop a style looping
back for a while. A price change applied via apply_prices.py sets this for you
(review is required on every price change), so review.py is for the no-change /
ad-hoc case. See STRATEGY.md.
"""

import os
import sys
import argparse
import psycopg2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import get_db_config

UPDATE = """
    UPDATE skusummary
    SET next_shopify_price_review = CURRENT_DATE + %(d)s
    WHERE groupid = %(g)s
    RETURNING next_shopify_price_review
"""


def main():
    ap = argparse.ArgumentParser(description="Park a groupid out of the triage for N days.")
    ap.add_argument("groupid")
    ap.add_argument("days", type=int, help="days from today to next review")
    args = ap.parse_args()
    if args.days < 0:
        sys.exit("days must be >= 0")

    conn = psycopg2.connect(**get_db_config())
    try:
        with conn.cursor() as cur:
            cur.execute(UPDATE, {"g": args.groupid, "d": args.days})
            row = cur.fetchone()
            if not row:
                sys.exit(f"no skusummary row for {args.groupid}")
            new_date = row[0]
        conn.commit()
    finally:
        conn.close()

    print(f"{args.groupid}: next review {new_date} (+{args.days}d) "
          f"- hidden from triage until then")


if __name__ == "__main__":
    main()
