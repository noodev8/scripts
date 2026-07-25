import sys
sys.path.insert(0, r'C:\scripts')
import psycopg2
from psycopg2.extras import RealDictCursor
from logging_utils import get_db_config

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor(cursor_factory=RealDictCursor)
G = '0040391-MADRID'

print(f"=== {G} (Brown Reg) — price_track price/sales/stock, last 45d ===")
cur.execute("""
    SELECT date, shopify_price, shopify_sales, shopify_stock
    FROM price_track WHERE groupid = %s
      AND date >= CURRENT_DATE - INTERVAL '45 days'
    ORDER BY date;
""", (G,))
for r in cur.fetchall():
    print(f"  {r['date']}  px={r['shopify_price']}  sales={r['shopify_sales']}  stock={r['shopify_stock']}")

print(f"\n=== {G} daily UNITS from sales table, last 45d ===")
cur.execute("""
    SELECT solddate::date AS d, SUM(qty) AS units,
           ROUND(AVG(soldprice)::numeric,2) AS avg_px
    FROM sales WHERE groupid = %s AND qty>0 AND soldprice>0
      AND solddate >= CURRENT_DATE - INTERVAL '45 days'
    GROUP BY 1 ORDER BY 1;
""", (G,))
for r in cur.fetchall():
    print(f"  {r['d']}  units={r['units']}  avg_px={r['avg_px']}")

print(f"\n=== Velocity pre vs post 2026-05-22 change ({G}) ===")
cur.execute("""
    SELECT
      SUM(qty) FILTER (WHERE solddate::date >= DATE '2026-05-08' AND solddate::date < DATE '2026-05-22') AS pre_14d,
      SUM(qty) FILTER (WHERE solddate::date >= DATE '2026-05-22') AS post_units,
      MIN(soldprice) FILTER (WHERE solddate::date >= DATE '2026-05-22') AS post_min_px,
      MAX(soldprice) FILTER (WHERE solddate::date >= DATE '2026-05-22') AS post_max_px
    FROM sales WHERE groupid = %s AND qty>0 AND soldprice>0;
""", (G,))
r = cur.fetchall()[0]
pre = r['pre_14d'] or 0
post = r['post_units'] or 0
print(f"  Pre-change  (08-21 May, 14d): {pre} units  = {pre/2:.1f}/wk")
print(f"  Post-change (22-29 May, 7d):  {post} units = {post:.1f}/wk")
print(f"  Post-change sold price range: {r['post_min_px']} - {r['post_max_px']}")

cur.close(); conn.close()
