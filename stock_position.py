#!/usr/bin/env python3
"""
STOCK POSITION REPORT
=====================

Totals the current stock position (units and cost value) for input into the
accounting system — the replacement for the legacy PowerBuilder stock button.

Definition (agreed with owner):
  - Local stock: localstock where deleted = 0 AND ordernum = '#FREE'.
    This is sellable, owned stock. Stock allocated to open orders (non-#FREE)
    is excluded because it is already accounted for in revenue.
    Amazon staging (location = 'C3-Amazon') is NOT added separately — those
    units already live in localstock as #FREE rows.
  - Amazon stock: amzfeed.amztotal (Amazon-held / FBA units, a separate
    physical location not represented in localstock).
  - Cost: skusummary.cost per groupid (NULL treated as 0.00).

This avoids the double-count present in the legacy PowerBuilder figure, which
added the C3-Amazon staging qty onto the Amazon side while also counting it in
the local count.

Output: Prints stock units and value to console.

Usage:
  python stock_position.py
"""

import psycopg2
from logging_utils import get_db_config

# Stock position: #FREE local stock + Amazon amztotal, valued at groupid cost.
# Aggregating to groupid before applying cost is equivalent to per-code valuation
# because every code in a groupid shares the same cost.
STOCK_POSITION_SQL = """
WITH local_free AS (
    SELECT groupid, SUM(qty) AS qty
    FROM localstock
    WHERE deleted = 0 AND ordernum = '#FREE'
    GROUP BY groupid
),
amz AS (
    SELECT groupid, SUM(amztotal) AS qty
    FROM amzfeed
    WHERE groupid IS NOT NULL
    GROUP BY groupid
),
gids AS (
    SELECT groupid FROM local_free
    UNION
    SELECT groupid FROM amz
)
SELECT
    COALESCE(SUM(COALESCE(lf.qty, 0) + COALESCE(a.qty, 0)), 0) AS units,
    COALESCE(SUM(
        (COALESCE(lf.qty, 0) + COALESCE(a.qty, 0)) * COALESCE(ss.cost::numeric, 0)
    ), 0) AS value
FROM gids g
LEFT JOIN local_free lf ON lf.groupid = g.groupid
LEFT JOIN amz        a  ON a.groupid  = g.groupid
LEFT JOIN skusummary ss ON ss.groupid = g.groupid;
"""


def get_stock_position():
    """Return (units, value) for the current stock position."""
    conn = psycopg2.connect(**get_db_config())
    try:
        cur = conn.cursor()
        cur.execute(STOCK_POSITION_SQL)
        units, value = cur.fetchone()
        return int(units), value
    finally:
        conn.close()


def report_stock_position():
    """Print the current stock position (units and value) to console."""
    units, value = get_stock_position()
    print(f"Stock Position: £{value:,.2f} ({units:,} units)")


def main():
    report_stock_position()
    return 0


if __name__ == "__main__":
    exit(main())
