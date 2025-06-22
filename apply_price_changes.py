#!/usr/bin/env python3
"""
Manual Price Change Application Tool
Allows easy application of specific price changes after review

USAGE:
python apply_price_changes.py GROUPID NEW_PRICE "REASON"
python apply_price_changes.py --bucket 1           # Apply all bucket 1 recommendations
python apply_price_changes.py --list-pending       # Show pending recommendations
python apply_price_changes.py --help               # Show usage help

Examples:
python apply_price_changes.py BIRK123 45.99 "Manual review - dead stock"
python apply_price_changes.py --bucket 1
"""

import psycopg2
import requests
import sys
import os
from datetime import datetime, date
from dotenv import load_dotenv
from logging_utils import manage_log_files, create_logger, get_db_config

# --- CONFIGURATION ---
load_dotenv('.env')

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in shopify_api.env file")

# Setup logging
SCRIPT_NAME = "apply_price_changes"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

def log_and_print(message):
    """Log message and also print to console"""
    log(message)
    print(f"{datetime.now().strftime('%H:%M:%S')} {message}")

def get_current_price(groupid):
    """Get current Shopify price for a product"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        cur.execute("SELECT shopifyprice FROM skusummary WHERE groupid = %s", (groupid,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result and result[0]:
            return float(result[0])
        else:
            return None
            
    except Exception as e:
        log_and_print(f"ERROR: Failed to get current price for {groupid}: {str(e)}")
        return None

def get_variant_by_groupid(groupid):
    """Get Shopify variant ID by groupid"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
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
            return None
            
    except Exception as e:
        log_and_print(f"ERROR: Failed to get variant for {groupid}: {str(e)}")
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
            log_and_print(f"ERROR: Shopify API error {response.status_code}: {response.text}")
            return False

    except Exception as e:
        log_and_print(f"ERROR: Failed to update Shopify price: {str(e)}")
        return False

def log_price_change(groupid, old_price, new_price, reason):
    """Log price change to database"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO price_change_log (groupid, old_price, new_price, reason, reviewed_by, change_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (groupid, old_price, new_price, reason, "MANUAL", date.today()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        log_and_print(f"ERROR: Failed to log price change for {groupid}: {str(e)}")
        return False

def apply_single_price_change(groupid, new_price, reason):
    """Apply a single price change"""
    log_and_print(f"Processing price change for {groupid}")
    
    # Get current price
    current_price = get_current_price(groupid)
    if current_price is None:
        log_and_print(f"ERROR: Could not get current price for {groupid}")
        return False

    # Check if price change is significant
    if abs(current_price - new_price) < 0.01:
        log_and_print(f"WARNING: Price change too small for {groupid} (£{abs(current_price - new_price):.2f})")
        return False

    # Get variant ID
    variant_id = get_variant_by_groupid(groupid)
    if not variant_id:
        log_and_print(f"ERROR: No variant ID found for {groupid}")
        return False

    # Update Shopify price
    success = update_shopify_price(variant_id, new_price)
    if not success:
        log_and_print(f"ERROR: Failed to update Shopify price for {groupid}")
        return False

    # Log the change
    log_success = log_price_change(groupid, current_price, new_price, reason)
    if not log_success:
        log_and_print(f"WARNING: Price updated but logging failed for {groupid}")

    log_and_print(f"SUCCESS: {groupid} price changed from £{current_price} to £{new_price}")
    return True

def get_pending_recommendations(bucket=None):
    """Get pending price change recommendations"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Read and execute the price drop SQL
        sql_file_path = os.path.join("performance_reports", "product_price_drop.sql")
        with open(sql_file_path, 'r') as f:
            sql_query = f.read()
        
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        # Convert to list of dictionaries and filter
        recommendations = []
        for row in results:
            item = dict(zip(columns, row))
            if item['bucket'] and (bucket is None or item['bucket'] == bucket):
                # Check if not recently changed
                cur.execute("""
                    SELECT COUNT(*) FROM price_change_log 
                    WHERE groupid = %s AND change_date >= CURRENT_DATE - INTERVAL '7 days'
                """, (item['groupid'],))
                
                recent_changes = cur.fetchone()[0]
                if recent_changes == 0:
                    recommendations.append(item)
        
        cur.close()
        conn.close()
        
        return recommendations
        
    except Exception as e:
        log(f"ERROR: Failed to get pending recommendations: {str(e)}")
        return []

def apply_bucket_changes(bucket):
    """Apply all changes for a specific bucket"""
    log(f"Applying all changes for bucket {bucket}")
    
    recommendations = get_pending_recommendations(bucket)
    if not recommendations:
        log(f"No pending recommendations found for bucket {bucket}")
        return
    
    log(f"Found {len(recommendations)} recommendations for bucket {bucket}")
    
    applied = 0
    failed = 0
    
    for item in recommendations:
        groupid = item['groupid']
        suggested_price = float(item['suggested_price'])
        bucket_reason = item['bucket_reason']
        
        success = apply_single_price_change(
            groupid, 
            suggested_price, 
            f"Bucket {bucket}: {bucket_reason}"
        )
        
        if success:
            applied += 1
        else:
            failed += 1
    
    log(f"Bucket {bucket} processing complete: {applied} applied, {failed} failed")

def list_pending_recommendations():
    """List all pending recommendations"""
    recommendations = get_pending_recommendations()
    
    if not recommendations:
        print("No pending recommendations found.")
        return
    
    print(f"\nPENDING PRICE CHANGE RECOMMENDATIONS ({len(recommendations)} total):")
    print("=" * 80)
    
    # Group by bucket
    by_bucket = {}
    for item in recommendations:
        bucket = item['bucket']
        if bucket not in by_bucket:
            by_bucket[bucket] = []
        by_bucket[bucket].append(item)
    
    for bucket in sorted(by_bucket.keys()):
        items = by_bucket[bucket]
        print(f"\nBUCKET {bucket} ({len(items)} items):")
        print("-" * 40)
        
        for item in items:
            current = float(item['current_price'])
            suggested = float(item['suggested_price'])
            savings = current - suggested
            print(f"  {item['groupid']}: £{current:.2f} -> £{suggested:.2f} (save £{savings:.2f})")
            print(f"    Stock: {item['stock']}, Days stale: {item['days_since_last_sold']}")
            print(f"    Reason: {item['bucket_reason']}")
            print()

def show_help():
    """Display usage help"""
    help_text = """
MANUAL PRICE CHANGE APPLICATION TOOL
====================================

USAGE:
  python apply_price_changes.py GROUPID NEW_PRICE "REASON"
  python apply_price_changes.py --bucket 1           # Apply all bucket 1 recommendations
  python apply_price_changes.py --list-pending       # Show pending recommendations
  python apply_price_changes.py --help               # Show this help

EXAMPLES:
  python apply_price_changes.py BIRK123 45.99 "Manual review - dead stock"
  python apply_price_changes.py --bucket 1
  python apply_price_changes.py --list-pending

BUCKET DESCRIPTIONS:
  1. Dead Stock - 180+ days no sales, stock >= 10
  2. Market Mismatch - Overpriced vs competitors  
  3. Stock Heavy - High stock, no benchmark
  4. Low Margin - Margin < £15
  5. Slow Mover - Moderate stock, stale

All changes are logged to price_change_log table and daily log files.
"""
    print(help_text)

def main():
    """Main execution function"""
    args = sys.argv[1:]
    
    if not args or "--help" in args or "-h" in args:
        show_help()
        return
    
    if "--list-pending" in args:
        list_pending_recommendations()
        return
    
    if "--bucket" in args:
        try:
            bucket_index = args.index("--bucket")
            bucket = int(args[bucket_index + 1])
            apply_bucket_changes(bucket)
        except (IndexError, ValueError):
            print("ERROR: --bucket requires a bucket number (1-5)")
        return
    
    # Single price change
    if len(args) < 3:
        print("ERROR: Single price change requires: GROUPID NEW_PRICE REASON")
        show_help()
        return
    
    groupid = args[0]
    try:
        new_price = float(args[1])
    except ValueError:
        print("ERROR: NEW_PRICE must be a valid number")
        return
    
    reason = args[2]
    
    success = apply_single_price_change(groupid, new_price, reason)
    if success:
        print(f"SUCCESS: Price change applied for {groupid}")
    else:
        print(f"FAILED: Could not apply price change for {groupid}")

if __name__ == "__main__":
    main()
