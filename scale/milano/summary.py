"""MILANO-SEG Summary — the entry report ("Summary").

The default manager Summary from ../SEGMENT_REPORTS.md, saved into the folder so
the drill chain (Summary -> drill 1 -> drill 2) is fully self-contained and
stepable. 30-day and 14-day windows, each with same-window YoY.

The table IS the report. Notes (segment_notes) are an on-request pull, not
pre-loaded here — per the manager-report template.

Run:  python scale/milano/summary.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

SEG = 'MILANO-SEG'
TODAY = date.today()

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()

cur.execute("SELECT groupid, colour, width, shopifyprice FROM skusummary "
            "WHERE segment=%s ORDER BY groupid", (SEG,))
items = cur.fetchall()
gids = [r[0] for r in items]


def window(days):
    start = TODAY - timedelta(days=days)
    cur.execute("""SELECT COALESCE(SUM(qty),0), COALESCE(SUM(qty*soldprice),0)
                   FROM sales WHERE groupid = ANY(%s) AND qty>0 AND soldprice>0
                   AND solddate::date >= %s AND solddate::date < %s""",
                (gids, start, TODAY))
    u, rev = cur.fetchone()
    ly_start = start.replace(year=start.year - 1)
    ly_end = TODAY.replace(year=TODAY.year - 1)
    cur.execute("""SELECT COALESCE(SUM(qty),0), COALESCE(SUM(qty*soldprice),0)
                   FROM sales WHERE groupid = ANY(%s) AND qty>0 AND soldprice>0
                   AND solddate::date >= %s AND solddate::date < %s""",
                (gids, ly_start, ly_end))
    lu, lrev = cur.fetchone()
    return u, rev, lu, lrev


print(f"=== {SEG} Summary  ({TODAY}) ===")
for gid, col, wid, px in items:
    print(f"  {gid:<22} {col or '-':<8} {wid or '-':<8} £{px}")
print()

print(f"{'Window':<14} {'Units':>6} {'U/day':>7} {'AvgPx':>8} {'Revenue':>10} {'YoYu':>6} {'YoYrev':>8}")
print("-" * 64)
for days in (30, 14):
    u, rev, lu, lrev = window(days)
    avg = (rev / u) if u else 0
    yoy_u = f"{(u-lu)/lu*100:+.0f}%" if lu else "n/a"
    yoy_r = f"{(rev-lrev)/lrev*100:+.0f}%" if lrev else "n/a"
    print(f"{'Last '+str(days)+'d':<14} {u:>6} {u/days:>7.2f} £{avg:>7.2f} £{rev:>9.0f} {yoy_u:>6} {yoy_r:>8}")

conn.close()
