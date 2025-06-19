#!/usr/bin/env python3
import psycopg2
from datetime import date, timedelta

DB_CONFIG = {
    "host": "77.68.13.150",
    "dbname": "brookfield_prod",
    "user": "brookfield_prod_user",
    "password": "prodpw",
    "port": 5432
}

def main():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1️⃣ SET DATES
        today = date.today()
        # We'll backfill the 7 days prior: 1 = yesterday, 7 = 7 days ago
        days_to_backfill = range(1, 8)

        # 2️⃣ DELETE any existing entry for `today` from price_track
        cur.execute("DELETE FROM price_track WHERE date = %s", (today,))
        # print(f"🗑️  Deleted existing entries for {today}")

        # 3️⃣ INSERT NEW ROWS for `today` (localstock only '#FREE')
        insert_stock_query = """
            INSERT INTO price_track (
                groupid,
                date,
                brand,
                amazon_stock,
                amazon_price,
                shopify_stock,
                shopify_price
            )
            SELECT
                s.groupid,
                %s AS date,
                s.brand,
                COALESCE(a.amzlive, 0)                                    AS amazon_stock,
                COALESCE(a.amzprice, 0)::numeric                          AS amazon_price,
                COALESCE(ls.total_qty, 0)
                  + COALESCE(a.amzlive, 0)
                  + COALESCE(u.total_stock, 0)                             AS shopify_stock,
                COALESCE(s.shopifyprice::numeric, 0)                       AS shopify_price
            FROM skusummary s
            LEFT JOIN (
                SELECT groupid, SUM(qty) AS total_qty
                FROM localstock
                WHERE deleted IS DISTINCT FROM 1
                  AND ordernum = '#FREE'
                GROUP BY groupid
            ) ls ON ls.groupid = s.groupid
            LEFT JOIN (
                SELECT
                    groupid,
                    MAX(amzprice)::numeric AS amzprice,
                    SUM(amzlive)        AS amzlive
                FROM amzfeed
                GROUP BY groupid
            ) a ON a.groupid = s.groupid
            LEFT JOIN (
                SELECT groupid, SUM(stock) AS total_stock
                FROM ukdstock
                GROUP BY groupid
            ) u ON u.groupid = s.groupid
            ;
        """
        cur.execute(insert_stock_query, (today,))
        conn.commit()
        print(f"✅ Inserted stock snapshot for {today} into price_track.")

        # Prepare the two update statements once:
        update_amazon_sales = """
            UPDATE price_track pt
            SET
                amazon_sales = a.total_qty,
                amazon_avg_sold_price = a.avg_price
            FROM (
                SELECT
                    groupid,
                    SUM(qty)                AS total_qty,
                    ROUND(AVG(soldprice)::numeric, 2) AS avg_price
                FROM sales
                WHERE solddate = %s
                  AND channel = 'AMZ'
                  AND qty > 0
                GROUP BY groupid
            ) a
            WHERE pt.groupid = a.groupid
              AND pt.date = %s
        ;
        """
        update_shopify_sales = """
            UPDATE price_track pt
            SET
                shopify_sales = s.total_qty,
                shopify_avg_sold_price = s.avg_price
            FROM (
                SELECT
                    groupid,
                    SUM(qty)                AS total_qty,
                    ROUND(AVG(soldprice)::numeric, 2) AS avg_price
                FROM sales
                WHERE solddate = %s
                  AND channel = 'SHP'
                  AND qty > 0
                GROUP BY groupid
            ) s
            WHERE pt.groupid = s.groupid
              AND pt.date = %s
        ;
        """

        # 4️⃣–5️⃣ Backfill sales for the last 7 days
        for delta in days_to_backfill:
            target_date = today - timedelta(days=delta)
            cur.execute(update_amazon_sales, (target_date, target_date))
            cur.execute(update_shopify_sales, (target_date, target_date))
            # print(f"↻ Backfilled sales for {target_date}")

        conn.commit()
        # print("✅ Sales backfill complete for the last 7 days.")

    except Exception as e:
        print("❌ Error occurred:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    main()

