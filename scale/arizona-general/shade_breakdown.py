"""ARIZONA-GENERAL shade breakdown — the queue view.

Standard report for analysing ARIZONA-GENERAL. One row per code, clustered by
colour (colours ordered by total demand, and within a colour the busiest shade
first), so promotion candidates float to the top and a shade's Reg/Nar pair sit
together. See ARIZONA-GENERAL.md for what it's for and how to read it.

GENERAL is the minor league: everything that isn't a colour brick yet —
seasonal dupes, material variants, shade experiments, fresh arrivals, tail.
The promotion unit is the shade-PAIR (Reg + Nar of one shade). When a pair reads as
a sustained, dominant seller, lift it into ARIZONA-<SHADE> — a human/style call off
the demand ranking, not a fixed revenue bar.

Run:  python scale/arizona-general/shade_breakdown.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

SEG = 'ARIZONA-GENERAL'
TODAY = date.today()
d90 = TODAY - timedelta(days=90)
d365 = TODAY - timedelta(days=365)

# Shade name parsed from the title: drop everything up to "... Sandals ", then
# the trailing " Regular/Narrow Fit". Label only — colour clustering is by the
# (rough) skusummary.colour field, not this string.
SHADE = (r"regexp_replace(regexp_replace(t.shopifytitle, '^.*Sandals ', ''), "
         r"'\s+(Regular|Narrow)\s+Fit.*$', '')")

SQL = rf"""
WITH base AS (
    SELECT ss.groupid, ss.colour, ss.shopifyprice AS px,
           {SHADE} AS shade,
           CASE WHEN t.shopifytitle ILIKE '%%Narrow Fit%%'  THEN 'Nar'
                WHEN t.shopifytitle ILIKE '%%Regular Fit%%' THEN 'Reg'
                ELSE '?' END AS fit,
           COALESCE(stk.stock,0)  AS stock,
           COALESCE(s90.u,0)      AS u90,
           COALESCE(s365.u,0)     AS u365,
           COALESCE(s365.rev,0)   AS rev365
    FROM skusummary ss
    LEFT JOIN title t ON t.groupid = ss.groupid
    LEFT JOIN (SELECT groupid, SUM(qty) AS stock FROM localstock
               WHERE ordernum='#FREE' AND deleted=0 AND qty>0 GROUP BY groupid) stk
           ON stk.groupid = ss.groupid
    LEFT JOIN (SELECT groupid, SUM(qty)::int AS u FROM sales
               WHERE qty>0 AND soldprice>0 AND solddate::date > %s GROUP BY groupid) s90
           ON s90.groupid = ss.groupid
    LEFT JOIN (SELECT groupid, SUM(qty)::int AS u, ROUND(SUM(qty*soldprice))::int AS rev
               FROM sales WHERE qty>0 AND soldprice>0 AND solddate::date > %s GROUP BY groupid) s365
           ON s365.groupid = ss.groupid
    WHERE ss.segment = %s
)
SELECT colour, shade, fit, groupid, px, stock, u90, u365, rev365,
       SUM(u365)  OVER (PARTITION BY colour)        AS col_u365,
       SUM(rev365) OVER (PARTITION BY colour)       AS col_rev,
       SUM(u365)  OVER (PARTITION BY colour, shade) AS shade_u365
FROM base
ORDER BY col_u365 DESC, colour,
         shade_u365 DESC, shade,
         CASE WHEN fit='Reg' THEN 0 ELSE 1 END
"""


def pxf(px):
    try:
        return float(px) if px not in (None, '') else 0.0
    except (TypeError, ValueError):
        return 0.0


conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()
cur.execute(SQL, (d90, d365, SEG))
rows = cur.fetchall()
conn.close()

print(f"=== {SEG} shade breakdown  ({TODAY}) ===")
print("Promotion = a human call off the ranking (no fixed revenue bar). "
      "Top rows = the queue; pair the shade names to read a candidate.\n")

hdr = (f"{'#':>2}  {'Colour':<7} {'Shade':<22} {'Fit':<3} {'GroupID':<18} "
       f"{'Px':>5} {'Stk':>4} {'u90':>4} {'u365':>5} {'Rev365':>8}")
print(hdr)
print("-" * len(hdr))

last_colour = None
pulse = {}
for i, r in enumerate(rows, 1):
    colour, shade, fit, gid, px, stock, u90, u365, rev365, col_u, col_rev, _ = r
    if last_colour is not None and colour != last_colour:
        print()  # blank line between colour clusters
    last_colour = colour
    pulse[colour or '-'] = (col_u, col_rev)
    print(f"{i:>2}  {(colour or '-'):<7} {(shade or '-')[:22]:<22} {fit:<3} "
          f"{gid:<18} £{pxf(px):>4.0f} {stock:>4} {u90:>4} {u365:>5} £{rev365:>6,}")

print("-" * len(hdr))
print("\nColour-level pulse (trailing 365d — coarse; the promotion unit is the shade-pair):")
for c, (u, rev) in sorted(pulse.items(), key=lambda x: -x[1][1]):
    print(f"  {c:<7} {u:>4} units  £{rev:>7,}")
