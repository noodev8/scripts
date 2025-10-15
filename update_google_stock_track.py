#!/usr/bin/env python3
"""
Google Stock Tracking Script
Calculates and records stock levels for Google Shopping campaign analysis.

Captures two metrics:
1. Live Stock: Products active on both Shopify and Google Merchant Centre
2. Total Stock: All products in inventory (localstock + Amazon)

Also imports Google Ads data from CSV file (adcost_summary_30.csv) if available.

This helps determine appropriate Google Shopping ad budget based on available inventory.
"""

import psycopg2
import csv
import os
from datetime import datetime
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "update_google_stock_track"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

def parse_csv_number(value):
    """
    Parse number from CSV, removing commas (thousands separator).

    Args:
        value: String value from CSV

    Returns:
        int or float: Parsed number
    """
    if not value or value.strip() == '':
        return 0
    # Remove commas and quotes
    cleaned = value.replace(',', '').replace('"', '').strip()
    try:
        # Try as integer first
        if '.' not in cleaned:
            return int(cleaned)
        return float(cleaned)
    except ValueError:
        log(f"WARNING: Could not parse number '{value}', using 0")
        return 0

def read_google_ads_csv(csv_path):
    """
    Read Google Ads CSV file and extract data.

    Expected format:
    Row 1: Title (skip)
    Row 2: Date range (skip)
    Row 3: Headers (Day,Clicks,Impr.,Currency code,Cost)
    Data rows: dates with metrics

    Args:
        csv_path: Path to CSV file

    Returns:
        list: List of dicts with date, clicks, impressions, cost
    """
    data = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)

            # Skip first 2 rows (title and date range)
            next(reader, None)
            next(reader, None)

            # Read header row (row 3)
            headers = next(reader, None)
            if not headers:
                log("ERROR: CSV file appears to be empty")
                return data

            log(f"CSV Headers: {headers}")

            # Read data rows
            for row in reader:
                if len(row) < 5:
                    log(f"WARNING: Skipping incomplete row: {row}")
                    continue

                try:
                    # Parse date (column 0)
                    date_str = row[0].strip()
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                    # Parse metrics
                    clicks = parse_csv_number(row[1])
                    impressions = parse_csv_number(row[2])
                    # Skip currency code (row[3])
                    cost = parse_csv_number(row[4])

                    data.append({
                        'date': date_obj,
                        'clicks': clicks,
                        'impressions': impressions,
                        'cost': cost
                    })

                except Exception as e:
                    log(f"ERROR: Failed to parse row {row}: {str(e)}")
                    continue

            log(f"Successfully parsed {len(data)} rows from CSV")
            return data

    except FileNotFoundError:
        log(f"INFO: CSV file not found: {csv_path}")
        return data
    except Exception as e:
        log(f"ERROR: Failed to read CSV file: {str(e)}")
        return data

def update_google_ads_data(cursor, csv_data):
    """
    Update google_stock_track records with Google Ads data.
    Only updates records that don't already have Google Ads data.

    Args:
        cursor: Database cursor
        csv_data: List of dicts with Google Ads metrics

    Returns:
        dict: Statistics (updated, skipped, not_found)
    """
    stats = {
        'updated': 0,
        'skipped': 0,
        'not_found': 0
    }

    for row in csv_data:
        # Check if record exists for this date
        check_query = """
        SELECT id, google_ad_spend, google_clicks, google_impressions
        FROM google_stock_track
        WHERE DATE(snapshot_date) = %s
        """

        try:
            cursor.execute(check_query, (row['date'],))
            result = cursor.fetchone()

            if not result:
                log(f"No stock tracking record found for {row['date']}")
                stats['not_found'] += 1
                continue

            record_id = result[0]
            existing_spend = result[1]
            existing_clicks = result[2]
            existing_impressions = result[3]

            # Skip if already has Google Ads data
            if existing_spend is not None:
                log(f"Record for {row['date']} already has Google Ads data, skipping")
                stats['skipped'] += 1
                continue

            # Update the record
            update_query = """
            UPDATE google_stock_track
            SET google_ad_spend = %s,
                google_clicks = %s,
                google_impressions = %s
            WHERE id = %s
            """

            cursor.execute(update_query, (
                row['cost'],
                row['clicks'],
                row['impressions'],
                record_id
            ))

            log(f"Updated {row['date']}: £{row['cost']:.2f}, {row['clicks']} clicks, {row['impressions']} impressions")
            stats['updated'] += 1

        except Exception as e:
            log(f"ERROR: Failed to update record for {row['date']}: {str(e)}")
            continue

    return stats

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
    """Main function to import Google Ads data and calculate/record stock levels"""
    log("=== GOOGLE STOCK TRACKING STARTED ===")
    start_time = datetime.now()

    conn = None
    cursor = None
    snapshot_created = False

    try:
        # Connect to database
        log("Connecting to database...")
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        log("Database connection established")

        # Step 1: Check if today's snapshot exists, create if needed
        if check_already_run_today(cursor):
            log("Stock snapshot already exists for today - skipping stock calculation")
        else:
            log("--- Calculating Live Stock (Shopify + Google) ---")
            live_units, live_value = calculate_live_stock(cursor)

            log("--- Calculating Total Stock (All Products) ---")
            total_units, total_value = calculate_total_stock(cursor)

            log("--- Calculating Yesterday's Shopify Sales ---")
            sales_units, sales_revenue = calculate_shopify_sales_yesterday(cursor)

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
                snapshot_created = True
                log("Stock snapshot created successfully")
            else:
                log("ERROR: Failed to insert snapshot, rolling back")
                conn.rollback()
                return 1

        # Step 2: Check for CSV file and import Google Ads data (independent of snapshot)
        csv_path = os.path.join(os.path.dirname(__file__), 'adcost_summary_30.csv')

        if os.path.exists(csv_path):
            log("--- Google Ads CSV File Found ---")
            log(f"Reading CSV file: {csv_path}")
            csv_data = read_google_ads_csv(csv_path)

            if csv_data:
                log("--- Updating Google Ads Data ---")
                stats = update_google_ads_data(cursor, csv_data)
                log(f"Google Ads import summary: {stats['updated']} updated, {stats['skipped']} skipped, {stats['not_found']} not found")
            else:
                log("WARNING: No data extracted from CSV file")
        else:
            log("INFO: No Google Ads CSV file found (adcost_summary_30.csv) - skipping ads data import")

        # Commit all changes (snapshot and/or CSV updates)
        conn.commit()
        log("All changes committed successfully")

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        log(f"=== GOOGLE STOCK TRACKING COMPLETED SUCCESSFULLY ===")
        log(f"Total execution time: {total_duration:.2f} seconds")
        return 0

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
