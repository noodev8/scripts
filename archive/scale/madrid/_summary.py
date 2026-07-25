import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import psycopg2
from datetime import date, timedelta
from logging_utils import get_db_config

SEG = 'MADRID-SEG'
TODAY = date.today()

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor()

cur.execute("SELECT groupid FROM skusummary WHERE segment = %s", (SEG,))
gids = [r[0] for r in cur.fetchall()]

def window(days, year_offset=0):
    end = TODAY - timedelta(days=365*year_offset)
    start = end - timedelta(days=days)
    cur.execute("""
        SELECT COALESCE(SUM(qty),0),
               COALESCE(SUM(qty*soldprice),0)
        FROM sales
        WHERE groupid = ANY(%s) AND qty>0 AND soldprice>0
          AND solddate::date > %s AND solddate::date <= %s
    """, (gids, start, end))
    u, rev = cur.fetchone()
    return int(u), float(rev)

print(f"=== {SEG} Summary  ({TODAY}) — {len(gids)} groupids ===\n")
print(f"{'Window':<14}{'Units':>7}{'U/day':>8}{'AvgPx':>8}{'Revenue':>11}{'YoY units':>11}{'YoY rev':>11}")
for label, days in [("Last 30 days", 30), ("Last 14 days", 14)]:
    u, rev = window(days, 0)
    uy, revy = window(days, 1)
    upd = u/days
    avg = rev/u if u else 0
    yoy_u = f"{(u-uy)/uy*100:+.0f}%" if uy else ("n/a" if u==0 else "new")
    yoy_r = f"{(rev-revy)/revy*100:+.0f}%" if revy else ("n/a" if rev==0 else "new")
    print(f"{label:<14}{u:>7}{upd:>8.2f}{avg:>7.0f}£{rev:>10,.0f}{yoy_u:>11}{yoy_r:>11}")

conn.close()
