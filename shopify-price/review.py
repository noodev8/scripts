#!/usr/bin/env python3
"""
Review  —  Shopify pricing strategy: park a groupid.

Sets groupid_performance.next_review_date (channel SHP) to today + <days>, so the
style drops out of the Stage 1 triage (latest_sales.py) until that date passes.

    python shopify-price/review.py 0129443-ARIZONA 7

Use it after a "no change" decision, or any time you want to stop a style looping
back for a while. A price change applied via apply_prices.py sets this for you
(review is required on every price change), so review.py is for the no-change /
ad-hoc case.

The same field is the system's cooldown gate: price_recommendation.py skips a
groupid whose next_review_date hasn't arrived, and it's shared with the
front-end's "Next Review". See STRATEGY.md.
"""

import os
import sys
import argparse
import psycopg2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import get_db_config

UPSERT = """
    INSERT INTO groupid_performance (groupid, channel, next_review_date)
    VALUES (%(g)s, 'SHP', CURRENT_DATE + %(d)s)
    ON CONFLICT (groupid, channel)
    DO UPDATE SET next_review_date = EXCLUDED.next_review_date
    RETURNING next_review_date
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
            cur.execute("SELECT 1 FROM skusummary WHERE groupid = %s", (args.groupid,))
            if not cur.fetchone():
                sys.exit(f"no skusummary row for {args.groupid}")
            cur.execute(UPSERT, {"g": args.groupid, "d": args.days})
            new_date = cur.fetchone()[0]
        conn.commit()
    finally:
        conn.close()

    print(f"{args.groupid}: next review {new_date} (+{args.days}d) "
          f"- hidden from triage until then")


if __name__ == "__main__":
    main()
