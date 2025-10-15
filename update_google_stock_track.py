#!/usr/bin/env python3
"""
Google Stock Tracking Script
Calculates and records stock levels for Google Shopping campaign analysis.

Captures two metrics:
1. Live Stock: Products active on both Shopify and Google Merchant Centre
2. Total Stock: All products in inventory (localstock + Amazon)

This helps determine appropriate Google Shopping ad budget based on available inventory.
"""

import psycopg2
from datetime import datetime
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "update_google_stock_track"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

def calculate_live_stock(cursor):
    """
    Calculate stock for products on both Shopify and Google Merchant Centre.

    Returns:
        tuple: (live_stock_units, live_stock_value)
    """
    query = """
    WITH localstock_agg AS (
        SELECT
            groupid,
            SUM(qty) as total_qty
        FROM localstock
        WHERE deleted = 0
        GROUP BY groupid
    ),
    amzfeed_agg AS (
        SELECT
            groupid,
            SUM(amzlive) as total_amzlive
        FROM amzfeed
        WHERE groupid IS NOT NULL
        GROUP BY groupid
    )
    SELECT
        COALESCE(SUM(
            COALESCE(ls.total_qty, 0) + COALESCE(af.total_amzlive, 0)
        ), 0) as live_stock_units,
        COALESCE(SUM(
            (COALESCE(ls.total_qty, 0) + COALESCE(af.total_amzlive, 0)) *
            COALESCE(ss.cost::NUMERIC, 0)
        ), 0) as live_stock_value
    FROM skusummary ss
    LEFT JOIN localstock_agg ls ON ss.groupid = ls.groupid
    LEFT JOIN amzfeed_agg af ON ss.groupid = af.groupid
    WHERE ss.shopify = 1
      AND ss.googlestatus = 1
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            units = int(result[0]) if result[0] is not None else 0
            value = float(result[1]) if result[1] is not None else 0.0
            log(f"Live stock calculated: {units} units, £{value:.2f} value")
            return units, value
        else:
            log("WARNING: No live stock data returned")
            return 0, 0.0

    except Exception as e:
        log(f"ERROR: Failed to calculate live stock: {str(e)}")
        raise

def calculate_total_stock(cursor):
    """
    Calculate total stock across all products (no filters).

    Returns:
        tuple: (total_stock_units, total_stock_value)
    """
    query = """
    WITH localstock_agg AS (
        SELECT
            groupid,
            SUM(qty) as total_qty
        FROM localstock
        WHERE deleted = 0
        GROUP BY groupid
    ),
    amzfeed_agg AS (
        SELECT
            groupid,
            SUM(amzlive) as total_amzlive
        FROM amzfeed
        WHERE groupid IS NOT NULL
        GROUP BY groupid
    )
    SELECT
        COALESCE(SUM(
            COALESCE(ls.total_qty, 0) + COALESCE(af.total_amzlive, 0)
        ), 0) as total_stock_units,
        COALESCE(SUM(
            (COALESCE(ls.total_qty, 0) + COALESCE(af.total_amzlive, 0)) *
            COALESCE(ss.cost::NUMERIC, 0)
        ), 0) as total_stock_value
    FROM skusummary ss
    LEFT JOIN localstock_agg ls ON ss.groupid = ls.groupid
    LEFT JOIN amzfeed_agg af ON ss.groupid = af.groupid
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            units = int(result[0]) if result[0] is not None else 0
            value = float(result[1]) if result[1] is not None else 0.0
            log(f"Total stock calculated: {units} units, £{value:.2f} value")
            return units, value
        else:
            log("WARNING: No total stock data returned")
            return 0, 0.0

    except Exception as e:
        log(f"ERROR: Failed to calculate total stock: {str(e)}")
        raise

def calculate_shopify_sales_yesterday(cursor):
    """
    Calculate Shopify sales from yesterday (CURRENT_DATE - 1).

    Returns:
        tuple: (units_sold, revenue)
    """
    query = """
    SELECT
        COALESCE(SUM(qty), 0) as units_sold,
        COALESCE(SUM(soldprice * qty), 0) as revenue
    FROM sales
    WHERE channel = 'SHP'
      AND solddate = CURRENT_DATE - 1
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            units = int(result[0]) if result[0] is not None else 0
            revenue = float(result[1]) if result[1] is not None else 0.0
            log(f"Yesterday's Shopify sales: {units} units, £{revenue:.2f} revenue")
            return units, revenue
        else:
            log("WARNING: No sales data returned for yesterday")
            return 0, 0.0

    except Exception as e:
        log(f"ERROR: Failed to calculate yesterday's sales: {str(e)}")
        raise

def insert_stock_snapshot(cursor, live_units, live_value, total_units, total_value, sales_units, sales_revenue):
    """
    Insert stock snapshot into google_stock_track table.

    Args:
        cursor: Database cursor
        live_units: Live stock unit count
        live_value: Live stock value
        total_units: Total stock unit count
        total_value: Total stock value
        sales_units: Yesterday's Shopify sales units
        sales_revenue: Yesterday's Shopify sales revenue
    """
    query = """
    INSERT INTO google_stock_track
        (live_stock_units, live_stock_value, total_stock_units, total_stock_value,
         shopify_units, shopify_sales, snapshot_date)
    VALUES
        (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    RETURNING id, snapshot_date
    """

    try:
        cursor.execute(query, (live_units, live_value, total_units, total_value, sales_units, sales_revenue))
        result = cursor.fetchone()

        if result:
            snapshot_id = result[0]
            snapshot_date = result[1]
            log(f"Stock snapshot inserted - ID: {snapshot_id}, Date: {snapshot_date}")

            # Calculate variance
            variance_units = total_units - live_units
            variance_value = total_value - live_value
            variance_pct = (live_units / total_units * 100) if total_units > 0 else 0

            log(f"Variance: {variance_units} units (£{variance_value:.2f}) not on Google/Shopify")
            log(f"Google/Shopify coverage: {variance_pct:.1f}% of total stock")

            return snapshot_id
        else:
            log("ERROR: Insert returned no data")
            return None

    except Exception as e:
        log(f"ERROR: Failed to insert stock snapshot: {str(e)}")
        raise

def check_already_run_today(cursor):
    """
    Check if the script has already run today.

    Returns:
        bool: True if already run today, False otherwise
    """
    query = """
    SELECT COUNT(*)
    FROM google_stock_track
    WHERE DATE(snapshot_date) = CURRENT_DATE
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        count = result[0] if result else 0

        if count > 0:
            log(f"WARNING: Script has already run {count} time(s) today")
            return True
        return False

    except Exception as e:
        log(f"ERROR: Failed to check if already run today: {str(e)}")
        raise

def main():
    """Main function to calculate and record stock levels"""
    log("=== GOOGLE STOCK TRACKING STARTED ===")
    start_time = datetime.now()

    conn = None
    cursor = None

    try:
        # Connect to database
        log("Connecting to database...")
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        log("Database connection established")

        # Check if already run today
        if check_already_run_today(cursor):
            log("Skipping execution - already run today")
            log("=== GOOGLE STOCK TRACKING SKIPPED ===")
            return 0

        # Calculate live stock (Shopify + Google)
        log("--- Calculating Live Stock (Shopify + Google) ---")
        live_units, live_value = calculate_live_stock(cursor)

        # Calculate total stock (all products)
        log("--- Calculating Total Stock (All Products) ---")
        total_units, total_value = calculate_total_stock(cursor)

        # Calculate yesterday's Shopify sales
        log("--- Calculating Yesterday's Shopify Sales ---")
        sales_units, sales_revenue = calculate_shopify_sales_yesterday(cursor)

        # Insert snapshot
        log("--- Inserting Stock Snapshot ---")
        snapshot_id = insert_stock_snapshot(
            cursor,
            live_units,
            live_value,
            total_units,
            total_value,
            sales_units,
            sales_revenue
        )

        if snapshot_id:
            # Commit transaction
            conn.commit()
            log("Transaction committed successfully")

            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            log(f"=== GOOGLE STOCK TRACKING COMPLETED SUCCESSFULLY ===")
            log(f"Total execution time: {total_duration:.2f} seconds")
        else:
            log("ERROR: Failed to insert snapshot, rolling back")
            conn.rollback()
            return 1

    except Exception as e:
        log(f"CRITICAL ERROR: Stock tracking failed: {str(e)}")
        if conn:
            try:
                conn.rollback()
                log("Database transaction rolled back")
            except:
                log("WARNING: Failed to rollback transaction")
        return 1

    finally:
        # Clean up database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        log("Database connection closed")

    return 0

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
