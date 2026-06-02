"""MILANO-SEG size breakdown — the further drill behind size_availability.py.

The style/width drill (size_availability.py) is one flat row per style/width.
This breaks each of those four rows down BY SIZE.

Layout: size-as-COLUMNS. One row per style/width (Brown Reg, Brown Nar, Black
Reg, Black Nar); one column per EU size. Each cell shows two metrics together:

    PRIMARY(BRACKET)      e.g.  5(3) = 5 sold in last 30 days, 3 in stock

Default pairing is units-30d with stock in brackets — recent demand leads, stock
cover sits beside it, so a high-demand low-stock size is obvious. Swap
PRIMARY / BRACKET (one line each) to view other pairings.

A '.' means that size doesn't exist for that style/width.
Size = the 2-digit suffix on skumap.code (e.g. '...-37'), always euro.

Run:  python scale/milano/size_breakdown.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

SEG = 'MILANO-SEG'
PRIMARY = 'u30'   # outside the bracket
BRACKET = 'stk'   # inside the bracket
LABELS = {'stk': 'in stock', 'u30': 'units 30d', 'u14': 'units 14d', 'wsh': 'future order'}

TODAY = date.today()
d14 = TODAY - timedelta(days=14)
d30 = TODAY - timedelta(days=30)

SQL = r"""
WITH seg AS (
    SELECT groupid, colour, width FROM skusummary WHERE segment = %s
),
codes AS (
    SELECT sm.code, seg.colour, seg.width,
           regexp_replace(sm.code, '^.*-', '')::int AS eu
    FROM skumap sm JOIN seg ON seg.groupid = sm.groupid
    WHERE sm.deleted = 0
),
stk AS (SELECT code, SUM(qty) AS v FROM localstock
        WHERE ordernum='#FREE' AND deleted=0 GROUP BY code),
s30 AS (SELECT code, SUM(qty)::int v FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date > %s GROUP BY code),
s14 AS (SELECT code, SUM(qty)::int v FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date > %s GROUP BY code),
bt AS (SELECT code, SUM(GREATEST(requested - invoiced, 0))::int AS v
       FROM birktracker GROUP BY code)
SELECT c.colour, c.width, c.eu,
       COALESCE(stk.v,0), COALESCE(s30.v,0), COALESCE(s14.v,0), COALESCE(bt.v,0)
FROM codes c
LEFT JOIN stk ON stk.code = c.code
LEFT JOIN s30 ON s30.code = c.code
LEFT JOIN s14 ON s14.code = c.code
LEFT JOIN bt  ON bt.code  = c.code
"""

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()
cur.execute(SQL, (SEG, d30, d14))
rows = cur.fetchall()
conn.close()

IDX = {'stk': 0, 'u30': 1, 'u14': 2, 'wsh': 3}
pi, bi = IDX[PRIMARY], IDX[BRACKET]

# (colour,width) -> {eu -> (primary, bracket)};  track which (style,eu) exist
grid = {}
all_eu = set()
exists = set()
STYLE_ORDER = [('Brown', 'Regular'), ('Brown', 'Narrow'),
               ('Black', 'Regular'), ('Black', 'Narrow')]
for colour, width, eu, stk, u30, u14, wsh in rows:
    vals = (stk, u30, u14, wsh)
    grid.setdefault((colour, width), {})[eu] = (vals[pi], vals[bi])
    exists.add((colour, width, eu))
    all_eu.add(eu)

eus = sorted(all_eu)
styles = [s for s in STYLE_ORDER if s in grid] + [s for s in grid if s not in STYLE_ORDER]

W = 7  # per-size cell width, fits e.g. "11(9)"
print(f"=== {SEG} size breakdown  ({TODAY}) ===")
print(f"cell = {PRIMARY}({BRACKET})  ->  {LABELS[PRIMARY]} ( {LABELS[BRACKET]} )  ·  '.' = size not in range\n")

hdr = f"{'Style':<16}" + "".join(f"{e:>{W}}" for e in eus) + f"{'Tot':>9}"
print(hdr)
print("-" * len(hdr))
for st in styles:
    colour, width = st
    row = grid[st]
    cells = ""
    tp = tb = 0
    for e in eus:
        if (colour, width, e) in exists:
            p, b = row.get(e, (0, 0))
            tp += p
            tb += b
            cells += f"{str(p)+'('+str(b)+')':>{W}}"
        else:
            cells += f"{'.':>{W}}"
    print(f"{colour+' '+width:<16}{cells}{str(tp)+'('+str(tb)+')':>9}")
