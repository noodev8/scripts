#!/usr/bin/env python3
"""
Google Ads CSV Import Script
Imports daily Google Ads cost, clicks, and impressions data from CSV file.

Only updates records that don't already have Google Ads data.
Matches by date with existing google_stock_track records.
"""

import psycopg2
import csv
import os
from datetime import datetime
from logging_utils import manage_log_files, create_logger, get_db_config

# Setup logging
SCRIPT_NAME = "import_google_ads_csv"
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
        log(f"ERROR: CSV file not found: {csv_path}")
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

def main():
    """Main function to import Google Ads CSV data"""
    log("=== GOOGLE ADS CSV IMPORT STARTED ===")
    start_time = datetime.now()

    # Check for CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'adcost_summary_30.csv')

    if not os.path.exists(csv_path):
        log(f"ERROR: CSV file not found at: {csv_path}")
        log("Please ensure 'adcost_summary_30.csv' is in the script directory")
        return 1

    log(f"Reading CSV file: {csv_path}")

    # Read CSV data
    csv_data = read_google_ads_csv(csv_path)

    if not csv_data:
        log("ERROR: No data read from CSV file")
        return 1

    conn = None
    cursor = None

    try:
        # Connect to database
        log("Connecting to database...")
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        log("Database connection established")

        # Update records
        log("--- Updating Google Ads Data ---")
        stats = update_google_ads_data(cursor, csv_data)

        # Commit transaction
        conn.commit()
        log("Transaction committed successfully")

        # Summary
        log(f"=== IMPORT SUMMARY ===")
        log(f"Updated: {stats['updated']} records")
        log(f"Skipped (already has data): {stats['skipped']} records")
        log(f"Not found (no stock track record): {stats['not_found']} records")

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        log(f"=== GOOGLE ADS CSV IMPORT COMPLETED SUCCESSFULLY ===")
        log(f"Total execution time: {total_duration:.2f} seconds")

        return 0

    except Exception as e:
        log(f"CRITICAL ERROR: Import failed: {str(e)}")
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

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
