"""MILANO-SEG availability — one row per style/width.

Originally cloned from scale/arizona-black/size_availability.py (per-EU-size),
but MILANO is read at style/width level: 4 codes = Brown + Black, each Reg + Nar.
This prints ONE FLAT TABLE, one row per code, no per-size breakdown.

Columns per row:
  Stk  = in stock (localstock, #FREE, deleted=0)
  u30  = units sold last 30 days
  u14  = units sold last 14 days
  Wsh  = requested - invoiced -> on a future order, the 6-month wishlist.
         Aspirational — do NOT treat as imminent stock.

See MILANO-SEG.md for the width codes.

Run:  python scale/milano/size_availability.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

SEG = 'MILANO-SEG'
TODAY = date.today()
d14 = TODAY - timedelta(days=14)
d30 = TODAY - timedelta(days=30)

SQL = r"""
WITH seg AS (
    SELECT groupid, colour, width, shopifyprice
    FROM skusummary WHERE segment = %s
),
stk AS (
    SELECT sm.groupid, SUM(ls.qty) AS stock
    FROM skumap sm
    JOIN localstock ls ON ls.code = sm.code AND ls.ordernum='#FREE' AND ls.deleted=0
    WHERE sm.deleted = 0
    GROUP BY sm.groupid
),
s30 AS (SELECT groupid, SUM(qty)::int u FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date > %s GROUP BY groupid),
s14 AS (SELECT groupid, SUM(qty)::int u FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date > %s GROUP BY groupid),
bt AS (
    SELECT SUBSTRING(code FROM '^[^-]+-[^-]+') AS groupid,
           SUM(GREATEST(requested - invoiced, 0))::int AS wish
    FROM birktracker GROUP BY 1
)
SELECT seg.colour, seg.width, seg.shopifyprice,
       COALESCE(stk.stock,0) AS stock,
       COALESCE(s30.u,0) AS u30,
       COALESCE(s14.u,0) AS u14,
       COALESCE(bt.wish,0) AS wish
FROM seg
LEFT JOIN stk  ON stk.groupid  = seg.groupid
LEFT JOIN s30  ON s30.groupid  = seg.groupid
LEFT JOIN s14  ON s14.groupid  = seg.groupid
LEFT JOIN bt   ON bt.groupid   = seg.groupid
ORDER BY CASE seg.colour WHEN 'Brown' THEN 0 WHEN 'Black' THEN 1 ELSE 2 END,
         CASE seg.width WHEN 'Regular' THEN 0 WHEN 'Narrow' THEN 1 ELSE 2 END
"""

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()
cur.execute(SQL, (SEG, d30, d14))
rows = cur.fetchall()
conn.close()


def pxf(p):
    try:
        return float(p) if p not in (None, '') else 0.0
    except (TypeError, ValueError):
        return 0.0


print(f"=== {SEG} availability  ({TODAY}) ===")
print("Stk=in stock  u30/u14=units sold  Wsh=on future order (6-month wishlist)\n")

print(f"{'Style':<16}{'Px':>8}{'Stk':>6}{'u30':>6}{'u14':>6}{'Wsh':>6}")
print("-" * 48)
tot = [0, 0, 0, 0]
for colour, width, px, stock, u30, u14, wish in rows:
    style = f"{colour or '?'} {width or '?'}"
    print(f"{style:<16}£{pxf(px):>6.2f}{stock:>6}{u30:>6}{u14:>6}{wish:>6}")
    for i, v in enumerate((stock, u30, u14, wish)):
        tot[i] += v
print("-" * 48)
print(f"{'Total':<16}{'':>8}{tot[0]:>6}{tot[1]:>6}{tot[2]:>6}{tot[3]:>6}")
