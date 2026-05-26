"""MAYARI-SEG stock-availability triage list.

Same shape as scale/eva/stock_triage.py — see scale/eva/EVA-SEG.md for
the philosophy. Sorted by total stock DESC so high-stock decisions sit
at the top (price/listing work) and stock-outs sit at the bottom
(drop further or wait for incoming).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

SEG = 'MAYARI-SEG'
TODAY = date.today()
d14 = TODAY - timedelta(days=14)
d30 = TODAY - timedelta(days=30)

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()

cur.execute("""
    WITH seg AS (
        SELECT groupid, colour, width, shopifyprice
        FROM skusummary WHERE segment = %s
    ),
    universe AS (
        SELECT sm.groupid, COUNT(DISTINCT sm.code) AS sizes_total
        FROM skumap sm JOIN seg ON seg.groupid = sm.groupid
        WHERE sm.deleted = 0
        GROUP BY sm.groupid
    ),
    instock AS (
        SELECT sm.groupid,
               COUNT(DISTINCT CASE WHEN ls.qty > 0 THEN sm.code END) AS sizes_in_stock,
               COALESCE(SUM(ls.qty), 0) AS units
        FROM skumap sm
        JOIN seg ON seg.groupid = sm.groupid
        LEFT JOIN localstock ls
          ON ls.code = sm.code AND ls.ordernum='#FREE' AND ls.deleted=0
        WHERE sm.deleted = 0
        GROUP BY sm.groupid
    ),
    s14 AS (
        SELECT groupid, SUM(qty) AS u, COALESCE(SUM(qty*soldprice)/NULLIF(SUM(qty),0),0) AS avgp
        FROM sales WHERE qty>0 AND soldprice>0 AND solddate::date >= %s
        GROUP BY groupid
    ),
    s30 AS (
        SELECT groupid, SUM(qty) AS u, COALESCE(SUM(qty*soldprice)/NULLIF(SUM(qty),0),0) AS avgp
        FROM sales WHERE qty>0 AND soldprice>0 AND solddate::date >= %s
        GROUP BY groupid
    ),
    incoming AS (
        SELECT SUBSTRING(bt.code FROM '^[^-]+-[^-]+') AS groupid,
               SUM(GREATEST(bt.requested - bt.arrived, 0))::int AS pending
        FROM birktracker bt
        WHERE bt.requested > bt.arrived
          AND bt.placedate IS NOT NULL
        GROUP BY 1
    ),
    latest_note AS (
        SELECT DISTINCT ON (pcl.groupid)
               pcl.groupid, pcl.change_date, pcl.reason_notes
        FROM price_change_log pcl
        JOIN seg ON seg.groupid = pcl.groupid
        WHERE pcl.reason_notes IS NOT NULL
          AND pcl.change_date >= %s
        ORDER BY pcl.groupid, pcl.change_date DESC, pcl.id DESC
    )
    SELECT seg.groupid, seg.colour, seg.width, seg.shopifyprice,
           u.sizes_total,
           i.sizes_in_stock,
           i.units AS stock_units,
           COALESCE(s30.u, 0) AS u30, ROUND(COALESCE(s30.avgp,0)::numeric, 0) AS avg30,
           COALESCE(s14.u, 0) AS u14, ROUND(COALESCE(s14.avgp,0)::numeric, 0) AS avg14,
           COALESCE(inc.pending, 0) AS incoming_units,
           ln.change_date, ln.reason_notes
    FROM seg
    LEFT JOIN universe u ON u.groupid = seg.groupid
    LEFT JOIN instock i  ON i.groupid = seg.groupid
    LEFT JOIN s14        ON s14.groupid = seg.groupid
    LEFT JOIN s30        ON s30.groupid = seg.groupid
    LEFT JOIN incoming inc ON inc.groupid = seg.groupid
    LEFT JOIN latest_note ln ON ln.groupid = seg.groupid
    ORDER BY i.units DESC NULLS LAST, COALESCE(s30.u,0) DESC
""", (SEG, d14, d30, TODAY - timedelta(days=180)))

rows = cur.fetchall()
conn.close()

print(f"=== {SEG} stock-availability triage  ({TODAY}) ===\n")
print(f"{'#':>2}  {'GroupID':<22} {'Colour/Fit':<20} {'Px':>4} {'Cov':>7} {'Stock':>5} {'u30':>4} {'u14':>4} {'Inc':>4}  {'Latest price note (<=180d)':<60}")
print("-" * 150)
for i, r in enumerate(rows, 1):
    gid, col, wid, px, sizes_t, sizes_in, stock, u30, a30, u14, a14, inc, ndate, note = r
    try:
        pxn = float(px) if px not in (None,'') else 0
    except (TypeError, ValueError):
        pxn = 0
    cw = f"{col or '-'} / {wid or '-'}"[:20]
    cov = f"{sizes_in or 0}/{sizes_t or 0}"
    inc_str = str(inc) if inc else "-"
    if note:
        note_trim = (note[:55] + '…') if len(note) > 56 else note
        note_str = f"{ndate} {note_trim}"
    else:
        note_str = "-"
    print(f"{i:>2}  {gid:<22} {cw:<20} £{pxn:>3.0f} {cov:>7} {stock or 0:>5} {u30:>4} {u14:>4} {inc_str:>4}  {note_str}")
