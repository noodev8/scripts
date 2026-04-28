#!/usr/bin/env python3
"""
Google Stock Tracking Script
Calculates and records stock levels for Google Shopping campaign analysis.

Creates daily snapshots dated for YESTERDAY with:
1. Live Stock: Products active on both Shopify and Google Merchant Centre
2. Total Stock: All products in inventory (localstock + Amazon)
3. Shopify Sales: Sales from the snapshot date (yesterday)
4. Birk Ad-Readiness: counts of READY styles, READY units, and THIN-selling styles
   (Birkenstock-only — definition matches BUDGET_REVIEW_PROCESS.md, single source of truth).
   Reflects current stock at script run-time (yesterday's row gets today's stock —
   same convention as live_stock_units).

Also imports Google Ads data from CSV file (adcost_summary_30.csv) if available.
The CSV data matches snapshot dates, ensuring no nulls in the database.

This helps determine appropriate Google Shopping ad budget based on available inventory
and historical performance.
"""

import psycopg2
import csv
import os
import shutil
from pathlib import Path
from datetime import datetime
from adcost_logging import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "update_google_stock_track"
CURRENT_TROAS = 400  # Current Google Ads target ROAS setting (%). Update when changed in Google Ads.
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
    Row 3: Headers (Day,Clicks,Impr.,Currency code,Cost,Search impr. share)
    Data rows: dates with metrics

    Args:
        csv_path: Path to CSV file

    Returns:
        list: List of dicts with date, clicks, impressions, cost, search_imp_share
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

                    # Parse search impression share (column 5, optional)
                    search_imp_share = None
                    if len(row) > 5:
                        share_str = row[5].strip().replace('%', '')
                        if share_str and share_str != '--':
                            try:
                                search_imp_share = float(share_str)
                            except ValueError:
                                log(f"WARNING: Could not parse search imp share '{row[5]}' for {date_str}")

                    data.append({
                        'date': date_obj,
                        'clicks': clicks,
                        'impressions': impressions,
                        'cost': cost,
                        'search_imp_share': search_imp_share
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
        SELECT id, google_ad_spend, google_clicks, google_impressions, google_search_imp_share, troas
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
            existing_imp_share = result[4]
            existing_troas = result[5]

            # If already has spend data, backfill any missing fields
            if existing_spend is not None:
                backfill_sets = []
                backfill_params = []

                if existing_imp_share is None and row.get('search_imp_share') is not None:
                    backfill_sets.append("google_search_imp_share = %s")
                    backfill_params.append(row['search_imp_share'])

                if existing_troas is None:
                    backfill_sets.append("troas = %s")
                    backfill_params.append(CURRENT_TROAS)

                if backfill_sets:
                    backfill_query = f"""
                    UPDATE google_stock_track
                    SET {', '.join(backfill_sets)}
                    WHERE id = %s
                    """
                    backfill_params.append(record_id)
                    cursor.execute(backfill_query, backfill_params)
                    log(f"Backfilled {row['date']}: {', '.join(backfill_sets)}")
                    stats['updated'] += 1
                else:
                    stats['skipped'] += 1
                continue

            # Update the record
            update_query = """
            UPDATE google_stock_track
            SET google_ad_spend = %s,
                google_clicks = %s,
                google_impressions = %s,
                google_search_imp_share = %s,
                troas = %s
            WHERE id = %s
            """

            cursor.execute(update_query, (
                row['cost'],
                row['clicks'],
                row['impressions'],
                row.get('search_imp_share'),
                CURRENT_TROAS,
                record_id
            ))

            share_str = f", {row.get('search_imp_share')}% imp share" if row.get('search_imp_share') else ""
            log(f"Updated {row['date']}: £{row['cost']:.2f}, {row['clicks']} clicks, {row['impressions']} impressions{share_str}")
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
    Matches the snapshot_date so all data on a row represents the same day.

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
            log(f"Sales from yesterday: {units} units, £{revenue:.2f} revenue")
            return units, revenue
        else:
            log("WARNING: No sales data returned")
            return 0, 0.0

    except Exception as e:
        log(f"ERROR: Failed to calculate sales: {str(e)}")
        raise

def calculate_birk_ad_readiness(cursor):
    """
    Calculate Birkenstock ad-readiness counts.

    Definition matches BUDGET_REVIEW_PROCESS.md (single source of truth).
    If the rule changes there, change it here too.

    - Universe: skusummary where brand='Birkenstock', segment NOT NULL/CRAP,
      shopify=1, googlestatus=1
    - Size universe: skumap where deleted=0 (DO NOT use skusummary.stockvariants
      or localstock for the denominator — both under-state the universe)
    - READY: sizes_in_stock/total_sizes >= 0.7 AND units >= 15
    - PARTIAL: sizes_in_stock/total_sizes >= 0.4 AND units >= 5 (and not READY)
    - THIN-selling: not READY/PARTIAL and sold_30d > 0 (the waste signal)

    Returns:
        dict: {birk_ready_styles, birk_ready_units, birk_thin_selling_styles}
    """
    query = """
    WITH size_universe AS (
        SELECT groupid, COUNT(DISTINCT code) AS total_sizes
        FROM skumap WHERE deleted = 0 GROUP BY groupid
    ),
    current_stock AS (
        SELECT groupid,
               SUM(qty) as units,
               COUNT(DISTINCT code) as sizes_in_stock
        FROM localstock
        WHERE ordernum = '#FREE' AND deleted = 0 AND qty > 0
        GROUP BY groupid
    ),
    recent_sales AS (
        SELECT groupid,
               SUM(CASE WHEN solddate >= CURRENT_DATE - 30 THEN qty ELSE 0 END) as sold_30d
        FROM sales
        WHERE channel = 'SHP' AND qty > 0
        GROUP BY groupid
    ),
    classified AS (
        SELECT
            ss.groupid,
            COALESCE(cs.units, 0) AS stock_now,
            COALESCE(rs.sold_30d, 0) AS sold_30d,
            CASE
                WHEN COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(su.total_sizes, 0) >= 0.7
                     AND COALESCE(cs.units, 0) >= 15 THEN 'READY'
                WHEN COALESCE(cs.sizes_in_stock, 0)::numeric / NULLIF(su.total_sizes, 0) >= 0.4
                     AND COALESCE(cs.units, 0) >= 5 THEN 'PARTIAL'
                ELSE 'THIN'
            END AS ad_readiness
        FROM skusummary ss
        LEFT JOIN size_universe su ON ss.groupid = su.groupid
        LEFT JOIN current_stock cs ON ss.groupid = cs.groupid
        LEFT JOIN recent_sales rs ON ss.groupid = rs.groupid
        WHERE ss.brand = 'Birkenstock'
          AND ss.segment IS NOT NULL
          AND ss.segment != 'CRAP'
          AND ss.shopify = 1
          AND ss.googlestatus = 1
    )
    SELECT
        COUNT(*) FILTER (WHERE ad_readiness = 'READY') AS ready_styles,
        COALESCE(SUM(stock_now) FILTER (WHERE ad_readiness = 'READY'), 0) AS ready_units,
        COUNT(*) FILTER (WHERE ad_readiness = 'THIN' AND sold_30d > 0) AS thin_selling_styles
    FROM classified
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            metrics = {
                'birk_ready_styles': int(result[0] or 0),
                'birk_ready_units': int(result[1] or 0),
                'birk_thin_selling_styles': int(result[2] or 0),
            }
            log(f"Birk ad-readiness: {metrics['birk_ready_styles']} READY "
                f"({metrics['birk_ready_units']} units), "
                f"{metrics['birk_thin_selling_styles']} THIN-selling")
            return metrics
        else:
            log("WARNING: No ad-readiness data returned")
            return {'birk_ready_styles': 0, 'birk_ready_units': 0, 'birk_thin_selling_styles': 0}

    except Exception as e:
        log(f"ERROR: Failed to calculate Birk ad-readiness: {str(e)}")
        raise

def backfill_birk_readiness_if_null(cursor, readiness):
    """
    If yesterday's snapshot exists with NULL readiness fields, populate them.

    Handles the deployment case (first script run after columns added) and
    any future case where a row was inserted before readiness tracking existed.
    Idempotent — only fires when fields are NULL.

    Returns:
        bool: True if a row was backfilled, False otherwise
    """
    query = """
    UPDATE google_stock_track
    SET birk_ready_styles = %(birk_ready_styles)s,
        birk_ready_units = %(birk_ready_units)s,
        birk_thin_selling_styles = %(birk_thin_selling_styles)s
    WHERE DATE(snapshot_date) = CURRENT_DATE - 1
      AND birk_ready_styles IS NULL
    RETURNING id
    """
    try:
        cursor.execute(query, readiness)
        result = cursor.fetchone()
        if result:
            log(f"Backfilled Birk ad-readiness on existing snapshot id {result[0]}")
            return True
        return False
    except Exception as e:
        log(f"ERROR: Failed to backfill Birk ad-readiness: {str(e)}")
        raise

def insert_stock_snapshot(cursor, metrics):
    """
    Insert stock snapshot into google_stock_track table for yesterday.

    Args:
        cursor: Database cursor
        metrics: dict with required keys —
            live_stock_units, live_stock_value,
            total_stock_units, total_stock_value,
            shopify_units, shopify_sales,
            birk_ready_styles, birk_ready_units, birk_thin_selling_styles
    """
    query = """
    INSERT INTO google_stock_track
        (live_stock_units, live_stock_value, total_stock_units, total_stock_value,
         shopify_units, shopify_sales, snapshot_date, troas,
         birk_ready_styles, birk_ready_units, birk_thin_selling_styles)
    VALUES
        (%(live_stock_units)s, %(live_stock_value)s,
         %(total_stock_units)s, %(total_stock_value)s,
         %(shopify_units)s, %(shopify_sales)s, CURRENT_DATE - 1, %(troas)s,
         %(birk_ready_styles)s, %(birk_ready_units)s, %(birk_thin_selling_styles)s)
    RETURNING id, snapshot_date
    """

    params = {**metrics, 'troas': CURRENT_TROAS}

    try:
        cursor.execute(query, params)
        result = cursor.fetchone()

        if result:
            snapshot_id = result[0]
            snapshot_date = result[1]
            log(f"Stock snapshot inserted - ID: {snapshot_id}, Date: {snapshot_date}")

            live_units = metrics['live_stock_units']
            live_value = metrics['live_stock_value']
            total_units = metrics['total_stock_units']
            total_value = metrics['total_stock_value']
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
    Check if snapshot for yesterday has already been created.

    Returns:
        bool: True if yesterday's snapshot exists, False otherwise
    """
    query = """
    SELECT COUNT(*)
    FROM google_stock_track
    WHERE DATE(snapshot_date) = CURRENT_DATE - 1
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        count = result[0] if result else 0

        if count > 0:
            log(f"Snapshot for yesterday already exists ({count} record(s))")
            return True
        return False

    except Exception as e:
        log(f"ERROR: Failed to check if yesterday's snapshot exists: {str(e)}")
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

        # Always compute Birk readiness — used for both insert and backfill paths
        log("--- Calculating Birk Ad-Readiness ---")
        readiness = calculate_birk_ad_readiness(cursor)

        # Step 1: Check if yesterday's snapshot exists, create if needed
        if check_already_run_today(cursor):
            log("Snapshot for yesterday already exists - skipping stock calculation")
            if backfill_birk_readiness_if_null(cursor, readiness):
                log("Birk readiness fields backfilled on existing snapshot")
        else:
            log("--- Creating Snapshot for Yesterday ---")
            log("--- Calculating Live Stock (Shopify + Google) ---")
            live_units, live_value = calculate_live_stock(cursor)

            log("--- Calculating Total Stock (All Products) ---")
            total_units, total_value = calculate_total_stock(cursor)

            log("--- Calculating Shopify Sales (Yesterday) ---")
            sales_units, sales_revenue = calculate_shopify_sales_yesterday(cursor)

            log("--- Inserting Stock Snapshot for Yesterday ---")
            metrics = {
                'live_stock_units': live_units,
                'live_stock_value': live_value,
                'total_stock_units': total_units,
                'total_stock_value': total_value,
                'shopify_units': sales_units,
                'shopify_sales': sales_revenue,
                **readiness,
            }
            snapshot_id = insert_stock_snapshot(cursor, metrics)

            if snapshot_id:
                snapshot_created = True
                log("Stock snapshot for yesterday created successfully")
            else:
                log("ERROR: Failed to insert snapshot, rolling back")
                conn.rollback()
                return 1

        # Step 2: Check for CSV file and import Google Ads data (independent of snapshot)
        csv_filename = 'adcost_summary_30.csv'
        csv_path = os.path.join(os.path.dirname(__file__), csv_filename)

        # Check Downloads folder for a fresh export and move it into place
        downloads_dir = os.environ.get('DOWNLOADS_DIR', str(Path.home() / 'Downloads'))
        downloads_csv = os.path.join(downloads_dir, csv_filename)
        if os.path.exists(downloads_csv):
            log(f"Found CSV in Downloads: {downloads_csv}")
            shutil.move(downloads_csv, csv_path)
            log(f"Moved to: {csv_path}")

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

            # Delete CSV after processing to avoid re-importing stale data
            try:
                os.remove(csv_path)
                log(f"Deleted processed CSV: {csv_path}")
            except OSError as e:
                log(f"WARNING: Could not delete CSV: {e}")
        else:
            log("INFO: No Google Ads CSV file found (checked script folder and Downloads) - skipping ads data import")

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
