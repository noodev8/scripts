#!/usr/bin/env python3
"""
Automated Price Drop System for Brookfield Comfort
Analyzes stagnant inventory and applies strategic price reductions

USAGE:
python price_drop_automation.py                    # Monitor mode (no changes)
python price_drop_automation.py --apply-bucket-1   # Apply bucket 1 changes only
python price_drop_automation.py --apply-all        # Apply all enabled buckets
python price_drop_automation.py --report-only      # Generate report file only
python price_drop_automation.py --help             # Show usage help
"""

import psycopg2
import requests
import sys
import time
import os
import json
from datetime import datetime, date
from dotenv import load_dotenv
from logging_utils import manage_log_files, create_logger, save_report_file, get_db_config

# --- CONFIGURATION ---
# Load environment variables from .env
load_dotenv('.env')

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

# Validate that the access token was loaded
if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in shopify_api.env file")

# Setup logging
SCRIPT_NAME = "price_drop_automation"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

# Import configuration
from price_drop_config import (
    ENABLE_PRICE_DROPS, ENABLE_BUCKET_1_AUTO, ENABLE_BUCKET_2_AUTO,
    ENABLE_BUCKET_3_AUTO, ENABLE_BUCKET_4_AUTO, ENABLE_BUCKET_5_AUTO,
    MAX_DAILY_CHANGES, MIN_PRICE_CHANGE, RECENT_CHANGE_COOLDOWN,
    BUCKET_CONFIG, get_enabled_buckets, is_bucket_enabled
)

# Log function is now created by logging_utils

def get_price_drop_analysis():
    """Execute the price drop SQL analysis and return results"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Read the SQL file
        sql_file_path = os.path.join("database", "product_price_drop.sql")
        with open(sql_file_path, 'r') as f:
            sql_query = f.read()
        
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        # Convert to list of dictionaries
        analysis_results = []
        for row in results:
            analysis_results.append(dict(zip(columns, row)))
        
        cur.close()
        conn.close()
        
        log(f"Price drop analysis completed: {len(analysis_results)} products analyzed")
        return analysis_results
        
    except Exception as e:
        log(f"ERROR: Failed to execute price drop analysis: {str(e)}")
        return []

def check_recent_price_changes(groupid, days=RECENT_CHANGE_COOLDOWN):
    """Check if product had recent price changes"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) FROM price_change_log 
            WHERE groupid = %s AND change_date >= CURRENT_DATE - INTERVAL '%s days'
        """, (groupid, days))
        
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return count > 0
        
    except Exception as e:
        log(f"ERROR: Failed to check recent price changes for {groupid}: {str(e)}")
        return True  # Assume recent change on error (safer)

def get_variant_by_groupid(groupid):
    """Get Shopify variant information by groupid"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Get variant link from skumap table
        cur.execute("""
            SELECT variantlink FROM skumap 
            WHERE groupid = %s AND variantlink IS NOT NULL 
            LIMIT 1
        """, (groupid,))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result and result[0]:
            return result[0]
        else:
            log(f"WARNING: No variant link found for groupid {groupid}")
            return None
            
    except Exception as e:
        log(f"ERROR: Failed to get variant for {groupid}: {str(e)}")
        return None

def update_shopify_price(variant_id, new_price):
    """Update price in Shopify via API"""
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/variants/{variant_id}.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    data = {
        "variant": {
            "id": variant_id,
            "price": str(new_price)
        }
    }
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return True
        else:
            log(f"ERROR: Shopify API error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log(f"ERROR: Failed to update Shopify price: {str(e)}")
        return False

def log_price_change(groupid, old_price, new_price, reason, applied=True):
    """Log price change to database and file"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Insert into price_change_log table
        cur.execute("""
            INSERT INTO price_change_log (groupid, old_price, new_price, reason, reviewed_by, change_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (groupid, old_price, new_price, reason, "AUTOMATION", date.today()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Log to file
        status = "APPLIED" if applied else "RECOMMENDED"
        log(f"{status}: {groupid} - {reason} - £{old_price} -> £{new_price}")
        
    except Exception as e:
        log(f"ERROR: Failed to log price change for {groupid}: {str(e)}")

def generate_report(analysis_results, mode="monitor"):
    """Generate detailed report of analysis and actions"""
    report_content = []
    report_content.append("PRICE DROP ANALYSIS REPORT")
    report_content.append("Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    report_content.append("Mode: " + mode.upper())
    report_content.append("=" * 60)
    report_content.append("")

    # Summary by bucket
    bucket_summary = {}
    for item in analysis_results:
        bucket = item.get('bucket')
        if bucket:
            if bucket not in bucket_summary:
                bucket_summary[bucket] = []
            bucket_summary[bucket].append(item)

    report_content.append("SUMMARY BY BUCKET:")
    report_content.append("-" * 30)
    for bucket in sorted(bucket_summary.keys()):
        items = bucket_summary[bucket]
        config = BUCKET_CONFIG.get(bucket, {})
        report_content.append(f"Bucket {bucket} ({config.get('name', 'Unknown')}): {len(items)} products")

    report_content.append("")
    report_content.append("=" * 60)
    report_content.append("")

    # Detailed listings
    for bucket in sorted(bucket_summary.keys()):
        items = bucket_summary[bucket]
        config = BUCKET_CONFIG.get(bucket, {})

        report_content.append(f"BUCKET {bucket}: {config.get('name', 'Unknown')} ({len(items)} products)")
        report_content.append("-" * 50)

        for item in items:
            report_content.append(f"GroupID: {item['groupid']}")
            report_content.append(f"  Current Price: £{item['current_price']}")
            report_content.append(f"  Suggested Price: £{item['suggested_price']}")
            report_content.append(f"  Stock: {item['stock']}")
            report_content.append(f"  Days Since Last Sold: {item['days_since_last_sold']}")
            report_content.append(f"  Reason: {item['bucket_reason']}")
            report_content.append("")

        report_content.append("")

    # Save report to logs directory
    report_filename = save_report_file("price_drop_report.txt", "\n".join(report_content))
    log(f"Report generated: {report_filename}")
    return report_filename

def process_price_changes(analysis_results, apply_changes=False, target_bucket=None):
    """Process price change recommendations"""
    changes_applied = 0
    changes_skipped = 0
    errors = 0

    log(f"Processing price changes - Apply: {apply_changes}, Target Bucket: {target_bucket}")

    for item in analysis_results:
        groupid = item['groupid']
        bucket = item['bucket']
        current_price = float(item['current_price'])
        suggested_price = float(item['suggested_price'])
        bucket_reason = item['bucket_reason']

        # Skip if no bucket assigned or targeting specific bucket
        if not bucket or (target_bucket and bucket != target_bucket):
            continue

        # Skip if price change is too small
        price_diff = abs(current_price - suggested_price)
        if price_diff < MIN_PRICE_CHANGE:
            log(f"SKIP: {groupid} - Price change too small (£{price_diff:.2f})")
            changes_skipped += 1
            continue

        # Check for recent price changes
        if check_recent_price_changes(groupid):
            log(f"SKIP: {groupid} - Recent price change detected")
            changes_skipped += 1
            continue

        # Check daily limit
        if changes_applied >= MAX_DAILY_CHANGES:
            log(f"SKIP: {groupid} - Daily change limit reached ({MAX_DAILY_CHANGES})")
            changes_skipped += 1
            continue

        # Determine if this bucket is enabled for automation
        bucket_enabled = apply_changes and is_bucket_enabled(bucket)

        # Get variant ID
        variant_id = get_variant_by_groupid(groupid)
        if not variant_id:
            log(f"ERROR: {groupid} - No variant ID found")
            errors += 1
            continue

        # Apply or log the change
        if bucket_enabled:
            # Apply the price change
            success = update_shopify_price(variant_id, suggested_price)
            if success:
                log_price_change(groupid, current_price, suggested_price,
                               f"Bucket {bucket}: {bucket_reason}", applied=True)
                changes_applied += 1
                log(f"APPLIED: {groupid} - £{current_price} -> £{suggested_price}")

                # Rate limiting
                time.sleep(0.5)
            else:
                log(f"ERROR: {groupid} - Failed to update Shopify price")
                errors += 1
        else:
            # Log recommendation only
            log_price_change(groupid, current_price, suggested_price,
                           f"Bucket {bucket}: {bucket_reason}", applied=False)
            log(f"RECOMMEND: {groupid} - £{current_price} -> £{suggested_price} ({bucket_reason})")

    return changes_applied, changes_skipped, errors

def cleanup_old_logs():
    """Remove old log files based on LOG_RETENTION setting"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not current_dir:
            current_dir = "."

        cutoff_date = datetime.now().date()
        cutoff_timestamp = datetime.combine(cutoff_date, datetime.min.time()).timestamp() - (LOG_RETENTION * 24 * 60 * 60)

        removed_count = 0
        for filename in os.listdir(current_dir):
            if filename.startswith("price_drop_") and filename.endswith(".log"):
                file_path = os.path.join(current_dir, filename)
                if os.path.getmtime(file_path) < cutoff_timestamp:
                    os.remove(file_path)
                    removed_count += 1

        if removed_count > 0:
            log(f"Cleaned up {removed_count} old log files")

    except Exception as e:
        log(f"WARNING: Failed to cleanup old logs: {str(e)}")

def show_help():
    """Display usage help"""
    help_text = """
PRICE DROP AUTOMATION SYSTEM
============================

USAGE:
  python price_drop_automation.py                    # Monitor mode (no changes)
  python price_drop_automation.py --apply-bucket-1   # Apply bucket 1 changes only
  python price_drop_automation.py --apply-all        # Apply all enabled buckets
  python price_drop_automation.py --report-only      # Generate report file only
  python price_drop_automation.py --help             # Show this help

SAFETY CONFIGURATION:
  Edit the script to enable automation:
  - ENABLE_PRICE_DROPS = True          # Master switch
  - ENABLE_BUCKET_1_AUTO = True        # Dead stock (180+ days)
  - ENABLE_BUCKET_2_AUTO = True        # Market mismatch
  - etc.

BUCKET DESCRIPTIONS:
  1. Dead Stock - 180+ days no sales, stock >= 10 (35% price reduction)
  2. Market Mismatch - Overpriced vs competitors (set to 98% of lowbench)
  3. Stock Heavy - High stock, no benchmark (25% reduction)
  4. Low Margin - Margin < £15 (set to cost + £0.01)
  5. Slow Mover - Moderate stock, stale (15% reduction)

LOG FILES:
  - price_drop_YYYY-MM-DD.log         # Daily activity log
  - price_drop_report_YYYY-MM-DD.txt  # Detailed analysis report

DATABASE LOGGING:
  All changes are logged to the 'price_change_log' table for tracking.
"""
    print(help_text)

def main():
    """Main execution function"""
    start_time = datetime.now()

    # Parse command line arguments
    args = sys.argv[1:]
    apply_changes = False
    target_bucket = None
    report_only = False

    if "--help" in args or "-h" in args:
        show_help()
        return

    if "--apply-bucket-1" in args:
        apply_changes = True
        target_bucket = 1
    elif "--apply-all" in args:
        apply_changes = True
    elif "--report-only" in args:
        report_only = True

    # Determine mode
    if report_only:
        mode = "report-only"
    elif apply_changes:
        mode = "apply" + (f"-bucket-{target_bucket}" if target_bucket else "-all")
    else:
        mode = "monitor"

    log(f"=== PRICE DROP AUTOMATION STARTED ===")
    log(f"Mode: {mode}")
    log(f"Master switch (ENABLE_PRICE_DROPS): {ENABLE_PRICE_DROPS}")
    log(f"Max daily changes: {MAX_DAILY_CHANGES}")

    # Get analysis results
    analysis_results = get_price_drop_analysis()
    if not analysis_results:
        log("ERROR: No analysis results obtained. Exiting.")
        return

    # Generate report
    report_file = generate_report(analysis_results, mode)

    if not report_only:
        # Process price changes
        changes_applied, changes_skipped, errors = process_price_changes(
            analysis_results, apply_changes, target_bucket
        )

        # Summary
        duration = datetime.now() - start_time
        duration_str = str(duration).split('.')[0]

        summary = f"COMPLETE - Mode: {mode}, Products analyzed: {len(analysis_results)}"
        summary += f", Changes applied: {changes_applied}, Skipped: {changes_skipped}"
        summary += f", Errors: {errors}, Duration: {duration_str}"
        log(summary)

        print(f"\nPrice Drop Automation Complete!")
        print(f"Mode: {mode}")
        print(f"Products analyzed: {len(analysis_results)}")
        print(f"Changes applied: {changes_applied}")
        print(f"Changes skipped: {changes_skipped}")
        print(f"Errors: {errors}")
        print(f"Report generated: {report_file}")
        print(f"Duration: {duration_str}")
    else:
        log(f"Report-only mode complete. Report: {report_file}")
        print(f"Report generated: {report_file}")

    # Cleanup old logs
    cleanup_old_logs()

if __name__ == "__main__":
    main()
