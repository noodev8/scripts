"""Pull EVA-SEG grid data from DB and push to segment tracker sheet as 'EVA-SEG Grid' tab.

Refresh-safe: drops and recreates the tab each run. No staff-edit columns yet — this is the
data layer only. State/action/rationale columns can be added later if the grid proves useful.
"""
import os
from datetime import date, datetime
from decimal import Decimal

import gspread
import psycopg2
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SHEET_ID = "1qc83UrqByH9gel9iOO6hYVqe6PDiA8GXZzEz-XWQtZ0"
TAB_NAME = "EVA-SEG Grid"
SERVICE_ACCOUNT_FILE = "merchant-feed-api-462809-23c712978791.json"

SQL = """
WITH seg AS (
    SELECT s.groupid, s.colour, s.width,
           SPLIT_PART(s.groupid, '-', 2) AS silhouette,
           t.shopifytitle,
           NULLIF(s.cost, '')::numeric AS cost,
           s.rrp::numeric AS rrp,
           s.shopifyprice::numeric AS price
    FROM skusummary s
    LEFT JOIN title t ON t.groupid = s.groupid
    WHERE s.segment = 'EVA-SEG'
),
sales_l4w AS (
    SELECT groupid, SUM(qty) AS units
    FROM sales
    WHERE qty > 0 AND soldprice > 0 AND channel <> 'CM3'
      AND solddate >= CURRENT_DATE - INTERVAL '28 days' AND solddate < CURRENT_DATE
      AND groupid IN (SELECT groupid FROM seg)
    GROUP BY groupid
),
sales_yoy AS (
    SELECT groupid, SUM(qty) AS units
    FROM sales
    WHERE qty > 0 AND soldprice > 0 AND channel <> 'CM3'
      AND solddate >= CURRENT_DATE - INTERVAL '1 year 28 days'
      AND solddate <  CURRENT_DATE - INTERVAL '1 year'
      AND groupid IN (SELECT groupid FROM seg)
    GROUP BY groupid
),
sales_lifetime AS (
    SELECT groupid, SUM(qty) AS units, MAX(solddate) AS last_sale
    FROM sales
    WHERE qty > 0 AND soldprice > 0 AND channel <> 'CM3'
      AND groupid IN (SELECT groupid FROM seg)
    GROUP BY groupid
),
stk AS (
    SELECT groupid,
           SUM(qty) AS stock_units,
           COUNT(DISTINCT code) AS sizes_in_stock
    FROM localstock
    WHERE ordernum = '#FREE' AND deleted = 0 AND qty > 0
      AND groupid IN (SELECT groupid FROM seg)
    GROUP BY groupid
),
universe AS (
    SELECT groupid, COUNT(DISTINCT code) AS total_sizes
    FROM skumap WHERE deleted = 0
      AND groupid IN (SELECT groupid FROM seg)
    GROUP BY groupid
),
dead AS (
    SELECT m.groupid, STRING_AGG(SPLIT_PART(m.code, '-', 3), ',' ORDER BY m.code) AS dead_codes
    FROM skumap m
    LEFT JOIN (
        SELECT DISTINCT groupid, code FROM localstock
        WHERE ordernum = '#FREE' AND deleted = 0 AND qty > 0
    ) ls ON ls.groupid = m.groupid AND ls.code = m.code
    WHERE m.deleted = 0
      AND m.groupid IN (SELECT groupid FROM seg)
      AND ls.code IS NULL
    GROUP BY m.groupid
)
SELECT
    sg.groupid,
    sg.shopifytitle,
    sg.silhouette,
    sg.colour,
    sg.width,
    sg.cost,
    sg.rrp,
    sg.price,
    ROUND(((sg.price * 0.96 - sg.cost) / NULLIF(sg.price,0) * 100), 1) AS margin_pct,
    COALESCE(sl.units, 0)  AS units_l4w,
    COALESCE(sy.units, 0)  AS units_yoy_4w,
    COALESCE(slt.units, 0) AS lifetime_units,
    slt.last_sale,
    COALESCE(st.stock_units, 0) AS stock,
    CASE WHEN COALESCE(sl.units, 0) > 0
         THEN ROUND((st.stock_units::numeric / (sl.units::numeric / 4)), 1) END AS wks_cover_l4w,
    CASE WHEN COALESCE(sy.units, 0) > 0
         THEN ROUND((st.stock_units::numeric / (sy.units::numeric / 4)), 1) END AS wks_cover_yoy,
    COALESCE(st.sizes_in_stock, 0) AS sizes_in,
    u.total_sizes AS sizes_total,
    CASE WHEN u.total_sizes > 0
         THEN ROUND(COALESCE(st.sizes_in_stock,0)::numeric / u.total_sizes::numeric * 100, 0) END AS size_cov_pct,
    d.dead_codes
FROM seg sg
LEFT JOIN sales_l4w      sl  ON sl.groupid  = sg.groupid
LEFT JOIN sales_yoy      sy  ON sy.groupid  = sg.groupid
LEFT JOIN sales_lifetime slt ON slt.groupid = sg.groupid
LEFT JOIN stk            st  ON st.groupid  = sg.groupid
LEFT JOIN universe       u   ON u.groupid   = sg.groupid
LEFT JOIN dead           d   ON d.groupid   = sg.groupid
ORDER BY
    CASE WHEN COALESCE(st.stock_units, 0) > 0 THEN 0 ELSE 1 END,
    sg.silhouette,
    COALESCE(st.stock_units, 0) DESC;
"""

HEADERS = [
    "groupid", "title", "silhouette", "colour", "width",
    "cost", "rrp", "price", "margin_%",
    "units_L4W", "units_YOY_4W", "lifetime_units", "last_sale",
    "stock", "wks_cover_L4W", "wks_cover_YOY",
    "sizes_in", "sizes_total", "size_cov_%", "dead_sizes",
]


def to_cell(v):
    if v is None:
        return ""
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (date, datetime)):
        return v.strftime("%Y-%m-%d")
    return v


def main():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()
    cur.execute(SQL)
    rows = cur.fetchall()
    conn.close()
    print(f"Pulled {len(rows)} rows from DB")

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"],
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)

    try:
        existing = sh.worksheet(TAB_NAME)
        sh.del_worksheet(existing)
        print(f"Removed existing '{TAB_NAME}' tab")
    except gspread.WorksheetNotFound:
        pass

    ws = sh.add_worksheet(title=TAB_NAME, rows=len(rows) + 5, cols=len(HEADERS))
    data = [HEADERS] + [[to_cell(v) for v in row] for row in rows]
    ws.update(values=data, range_name="A1", value_input_option="USER_ENTERED")
    ws.freeze(rows=1)
    print(f"Wrote {len(rows)} rows to '{TAB_NAME}' tab")


if __name__ == "__main__":
    main()
