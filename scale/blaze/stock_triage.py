"""BLAZE-SEG stock-availability triage (Amazon / FBA).

Self-contained — BLAZE's own copy. Amazon-flavoured, NOT the Birk shape:
  Stock = live FBA units (amzfeed.amzlive) — what actually drives sales.
  Send  = warehouse #FREE units available to ship into FBA. Lunar's 4-day
          reorder makes this the live lever (unlike Birk's 6-month birktracker).
  OOS   = sizes that sold in the last 30d but are now ZERO at FBA — the
          demand the listing currently can't convert.

Sorted by u30 DESC so the strongest sellers surface first and any that are
OOS-on-hot-size are obvious at the top.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

SEG = 'BLAZE-SEG'
TODAY = date.today()
d14 = TODAY - timedelta(days=14)
d30 = TODAY - timedelta(days=30)

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()

cur.execute("""
    WITH seg AS (
        SELECT groupid, colour, shopifyprice
        FROM skusummary WHERE segment = %s
    ),
    universe AS (
        SELECT sm.groupid, COUNT(DISTINCT sm.code) AS sizes_total
        FROM skumap sm JOIN seg ON seg.groupid = sm.groupid
        WHERE sm.deleted = 0
        GROUP BY sm.groupid
    ),
    fba AS (  -- live FBA per code
        SELECT sm.groupid, sm.code, RIGHT(sm.code, 2) AS sz,
               COALESCE(af.amzlive, 0) AS qty,
               NULLIF(af.amzprice, '')::numeric AS amzprice
        FROM skumap sm
        JOIN seg ON seg.groupid = sm.groupid
        LEFT JOIN amzfeed af ON af.code = sm.code
        WHERE sm.deleted = 0
    ),
    fba_g AS (
        SELECT groupid,
               COUNT(DISTINCT CASE WHEN qty > 0 THEN code END) AS sizes_in_stock,
               SUM(qty) AS units,
               ROUND(AVG(amzprice)::numeric, 2) AS px
        FROM fba GROUP BY groupid
    ),
    whse AS (  -- warehouse #FREE units sendable to FBA
        SELECT sm.groupid, COALESCE(SUM(ls.qty), 0) AS units
        FROM skumap sm
        JOIN seg ON seg.groupid = sm.groupid
        LEFT JOIN localstock ls
          ON ls.code = sm.code AND ls.ordernum='#FREE' AND ls.deleted=0
        WHERE sm.deleted = 0
        GROUP BY sm.groupid
    ),
    sold30c AS (
        SELECT code, SUM(qty) AS u FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date >= %s GROUP BY code
    ),
    oos AS (  -- sizes sold in 30d but now 0 at FBA
        SELECT f.groupid, STRING_AGG(f.sz, ',' ORDER BY f.sz) AS oos_sizes
        FROM fba f JOIN sold30c s ON s.code = f.code
        WHERE f.qty = 0 AND s.u > 0
        GROUP BY f.groupid
    ),
    s14 AS (
        SELECT groupid, SUM(qty) AS u FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date >= %s GROUP BY groupid
    ),
    s30 AS (
        SELECT groupid, SUM(qty) AS u FROM sales
        WHERE qty>0 AND soldprice>0 AND solddate::date >= %s GROUP BY groupid
    )
    SELECT seg.groupid, seg.colour, seg.shopifyprice,
           u.sizes_total, fg.sizes_in_stock, fg.units AS fba_units, fg.px,
           w.units AS whse_units,
           COALESCE(s30.u, 0) AS u30, COALESCE(s14.u, 0) AS u14,
           o.oos_sizes
    FROM seg
    LEFT JOIN universe u ON u.groupid = seg.groupid
    LEFT JOIN fba_g fg   ON fg.groupid = seg.groupid
    LEFT JOIN whse w     ON w.groupid = seg.groupid
    LEFT JOIN s14        ON s14.groupid = seg.groupid
    LEFT JOIN s30        ON s30.groupid = seg.groupid
    LEFT JOIN oos o      ON o.groupid = seg.groupid
    ORDER BY COALESCE(s30.u, 0) DESC, fg.units DESC NULLS LAST
""", (SEG, d30, d14, d30))

rows = cur.fetchall()
conn.close()

print(f"=== {SEG} stock-availability triage  (Amazon/FBA - {TODAY}) ===\n")
print(f"{'#':>2}  {'GroupID':<22} {'Colour':<8} {'Px':>6} {'Cov':>6} {'FBA':>4} {'u30':>4} {'u14':>4} {'Send':>4}  {'OOS(hot)':<12}")
print("-" * 90)
for i, r in enumerate(rows, 1):
    gid, col, shop_px, sizes_t, sizes_in, fba_u, px, whse_u, u30, u14, oos = r
    px_str = f"£{float(px):.2f}" if px is not None else "-"
    cov = f"{sizes_in or 0}/{sizes_t or 0}"
    send_str = str(whse_u) if whse_u else "-"
    oos_str = oos or "-"
    print(f"{i:>2}  {gid:<22} {col or '-':<8} {px_str:>6} {cov:>6} {fba_u or 0:>4} {u30:>4} {u14:>4} {send_str:>4}  {oos_str:<12}")

print(f"\nShopify list price (reference, not the Amazon sell price): "
      f"£{rows[0][2] if rows else '-'}")
