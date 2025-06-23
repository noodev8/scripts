#!/usr/bin/env python3
import psycopg2
from datetime import date, timedelta
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "price_track"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

def main():
    conn = None
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # STEP 1: SET DATES
        today = date.today()
        # We'll backfill the 7 days prior: 1 = yesterday, 7 = 7 days ago
        days_to_backfill = range(1, 8)

        # STEP 2: DELETE any existing entry for `today` from price_track
        cur.execute("DELETE FROM price_track WHERE date = %s", (today,))

        # STEP 3: INSERT NEW ROWS for `today` (localstock only '#FREE')
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
        print(f"Inserted stock snapshot for {today} into price_track.")

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

        # STEP 4-5: Backfill sales for the last 7 days
        for delta in days_to_backfill:
            target_date = today - timedelta(days=delta)
            cur.execute(update_amazon_sales, (target_date, target_date))
            cur.execute(update_shopify_sales, (target_date, target_date))
            # print(f"↻ Backfilled sales for {target_date}")

        conn.commit()

        # Single clear log entry
        log(f"Price track updated for {today}")

    except Exception as e:
        log(f"ERROR: Price track update failed: {str(e)}")
        print("ERROR occurred:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    main()

