"""ARIZONA-TAUPE size-availability — the in-season core-size view.

The brick drill. A 2-code colour brick (Reg + Nar) doesn't need a per-groupid
triage — it needs a per-SIZE picture: which sizes are in stock, which are
selling, and crucially what stock can be pulled forward IN-SEASON vs what's
stuck on the 6-month order cycle.

Two incoming columns, from birktracker, kept deliberately separate:
  Inv  = invoiced - arrived  -> billed, not yet received. RELEASABLE NOW by
         paying the outstanding invoice. This is the in-season lever.
  Wish = requested - invoiced -> on a future order, not yet billed. The 6-month
         wishlist. Aspirational — do NOT treat as imminent stock.

Size = the 2-digit suffix on skumap.code (e.g. '...-37'), which is ALWAYS the
euro size by design. We do not use skumap.uksize or skumap.eurosize.

See ARIZONA-TAUPE.md. To clone for another brick, copy the folder and change SEG.

Run:  python scale/arizona-taupe/size_availability.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

SEG = 'ARIZONA-TAUPE'
TODAY = date.today()
d14 = TODAY - timedelta(days=14)
d30 = TODAY - timedelta(days=30)

SQL = r"""
WITH seg AS (
    SELECT groupid FROM skusummary WHERE segment = %s
),
codes AS (
    SELECT sm.code, sm.groupid,
           regexp_replace(sm.code, '^.*-', '') AS eu,
           CASE WHEN ss.width ILIKE 'Narrow'  OR t.shopifytitle ILIKE '%%Narrow Fit%%'  THEN 'Nar'
                WHEN ss.width ILIKE 'Regular' OR t.shopifytitle ILIKE '%%Regular Fit%%' THEN 'Reg'
                ELSE '?' END AS fit,
           ss.shopifyprice AS px
    FROM skumap sm
    JOIN seg ON seg.groupid = sm.groupid
    JOIN skusummary ss ON ss.groupid = sm.groupid
    LEFT JOIN title t ON t.groupid = sm.groupid
    WHERE sm.deleted = 0
),
stk AS (
    SELECT code, SUM(qty) AS stock FROM localstock
    WHERE ordernum='#FREE' AND deleted=0 GROUP BY code
),
s30 AS (SELECT code, SUM(qty)::int u FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date > %s GROUP BY code),
s14 AS (SELECT code, SUM(qty)::int u FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date > %s GROUP BY code),
bt AS (
    SELECT code,
           SUM(GREATEST(invoiced - arrived, 0))::int  AS inv,
           SUM(GREATEST(requested - invoiced, 0))::int AS wish
    FROM birktracker GROUP BY code
)
SELECT c.fit, c.eu, c.px,
       COALESCE(stk.stock,0) AS stock,
       COALESCE(s30.u,0) AS u30,
       COALESCE(s14.u,0) AS u14,
       COALESCE(bt.inv,0) AS inv,
       COALESCE(bt.wish,0) AS wish
FROM codes c
LEFT JOIN stk ON stk.code = c.code
LEFT JOIN s30 ON s30.code = c.code
LEFT JOIN s14 ON s14.code = c.code
LEFT JOIN bt  ON bt.code  = c.code
ORDER BY c.eu::int
"""

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()
cur.execute(SQL, (SEG, d30, d14))
rows = cur.fetchall()
conn.close()

# pivot: size -> {fit -> metrics}, plus per-fit price
sizes, px = {}, {}
fits_seen = []
for fit, eu, p, stock, u30, u14, inv, wish in rows:
    sizes.setdefault(eu, {})[fit] = (stock, u30, u14, inv, wish)
    if fit not in fits_seen and fit != '?':
        fits_seen.append(fit)
    px[fit] = p

FITS = [f for f in ('Reg', 'Nar') if f in fits_seen] or fits_seen


def pxf(p):
    try:
        return float(p) if p not in (None, '') else 0.0
    except (TypeError, ValueError):
        return 0.0


print(f"=== {SEG} size availability  ({TODAY}) ===")
print("  ".join(f"{f} £{pxf(px.get(f)):.0f}" for f in FITS))
print("Stk=in stock  u30/u14=units sold  Inv=invoiced-not-arrived (releasable now)  "
      "Wsh=on future order (6-month wishlist)\n")

cell = f"{'Stk':>4}{'u30':>4}{'u14':>4}{'Inv':>4}{'Wsh':>4}"
top = f"{'EU':>3} | " + " | ".join(f"{f:<20}" for f in FITS)
sub = f"{'':>3} | " + " | ".join(cell for _ in FITS)
print(top)
print(sub)
print("-" * len(sub))

tot = {f: [0, 0, 0, 0, 0] for f in FITS}
for eu in sorted(sizes, key=lambda x: int(x)):
    line = f"{eu:>3} | "
    parts = []
    for f in FITS:
        m = sizes[eu].get(f)
        if m:
            for i, v in enumerate(m):
                tot[f][i] += v
            parts.append(f"{m[0]:>4}{m[1]:>4}{m[2]:>4}{m[3]:>4}{m[4]:>4}")
        else:
            parts.append(f"{'-':>4}{'-':>4}{'-':>4}{'-':>4}{'-':>4}")
    print(line + " | ".join(parts))

print("-" * len(sub))
tline = f"{'Tot':>3} | "
print(tline + " | ".join(f"{t[0]:>4}{t[1]:>4}{t[2]:>4}{t[3]:>4}{t[4]:>4}" for f, t in tot.items()))
