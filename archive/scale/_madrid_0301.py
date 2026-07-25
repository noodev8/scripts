import sys
sys.path.insert(0, r'C:\scripts')
import psycopg2
from psycopg2.extras import RealDictCursor
from logging_utils import get_db_config

conn = psycopg2.connect(**get_db_config())
cur = conn.cursor(cursor_factory=RealDictCursor)
G = '0040301-MADRID'

# Names of all MADRID groupids for labelling (price from skusummary, name from sales)
print("=== MADRID groupid names ===")
cur.execute("""
    SELECT s.groupid, s.shopifyprice,
           (SELECT productname FROM sales x WHERE x.groupid=s.groupid
             ORDER BY solddate DESC LIMIT 1) AS productname
    FROM skusummary s WHERE s.segment ILIKE '%MADRID%' ORDER BY s.groupid;
""")
for r in cur.fetchall():
    print(f"  {r['groupid']:18} px={r['shopifyprice']}  {r['productname']}")

print(f"\n=== {G}: price_track price/sales/stock, last 45d ===")
cur.execute("""
    SELECT date, shopify_price, shopify_sales, shopify_stock
    FROM price_track WHERE groupid = %s
      AND date >= CURRENT_DATE - INTERVAL '45 days'
    ORDER BY date;
""", (G,))
for r in cur.fetchall():
    print(f"  {r['date']}  px={r['shopify_price']}  sales={r['shopify_sales']}  stock={r['shopify_stock']}")

print(f"\n=== {G}: daily UNITS (sales table), last 60d ===")
cur.execute("""
    SELECT solddate::date AS d, SUM(qty) AS units, ROUND(AVG(soldprice)::numeric,2) AS avg_px
    FROM sales WHERE groupid = %s AND qty>0 AND soldprice>0
      AND solddate >= CURRENT_DATE - INTERVAL '60 days'
    GROUP BY 1 ORDER BY 1;
""", (G,))
for r in cur.fetchall():
    print(f"  {r['d']}  units={r['units']}  avg_px={r['avg_px']}")

print(f"\n=== {G}: rate windows + all-time price points ===")
cur.execute("""
    SELECT
      SUM(qty) FILTER (WHERE solddate >= CURRENT_DATE - INTERVAL '14 days') AS u14,
      SUM(qty) FILTER (WHERE solddate >= CURRENT_DATE - INTERVAL '30 days') AS u30,
      SUM(qty) FILTER (WHERE solddate >= CURRENT_DATE - INTERVAL '90 days') AS u90,
      MIN(solddate)::date AS first_sale, MAX(solddate)::date AS last_sale
    FROM sales WHERE groupid = %s AND qty>0 AND soldprice>0;
""", (G,))
r = cur.fetchall()[0]
print(f"  u14={r['u14'] or 0} ({(r['u14'] or 0)/2:.1f}/wk)  u30={r['u30'] or 0}  u90={r['u90'] or 0}")
print(f"  first_sale={r['first_sale']}  last_sale={r['last_sale']}")

print(f"\n=== {G}: units by sold price (last 12m) — where has it sold before? ===")
cur.execute("""
    SELECT soldprice, SUM(qty) AS units, MIN(solddate)::date AS first, MAX(solddate)::date AS last
    FROM sales WHERE groupid = %s AND qty>0 AND soldprice>0
      AND solddate >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY soldprice ORDER BY soldprice;
""", (G,))
for r in cur.fetchall():
    print(f"  £{r['soldprice']}  units={r['units']}  ({r['first']} .. {r['last']})")

cur.close(); conn.close()
