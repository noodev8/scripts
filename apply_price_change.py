#!/usr/bin/env python3
"""
Brookfield Comfort Bulk Price Change Applicator
Reads approved CSV file and applies price changes to Shopify and Google.
"""

import sys
import os
import csv
import psycopg2
import subprocess
from datetime import datetime
from logging_utils import get_db_config, create_logger

# Setup logging
log = create_logger("apply_bulk_price_changes")

# Shopify config no longer needed - price_update.py handles all API configurations

def read_approved_changes(csv_filename):
    """Read CSV file and return approved changes"""
    approved_changes = []
    
    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Check if approved (user entered '1' in approve column)
                if row.get('approve', '').strip() == '1':
                    approved_changes.append(row)
        
        log(f"Loaded {len(approved_changes)} approved changes from {csv_filename}")
        return approved_changes
        
    except Exception as e:
        log(f"ERROR: Failed to read CSV file: {str(e)}")
        return []

# Removed separate Shopify functions - now using price_update.py for both platforms

def update_database_price(groupid, new_price):
    """Update price in local database and set shopifychange flag"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Update skusummary table with new price and set shopifychange flag
        cur.execute("""
            UPDATE skusummary
            SET shopifyprice = %s, shopifychange = 1
            WHERE groupid = %s
        """, (new_price, groupid))

        conn.commit()
        cur.close()
        conn.close()

        log(f"SUCCESS: Updated database price for {groupid} to £{new_price} and set shopifychange flag")
        return True

    except Exception as e:
        log(f"ERROR: Failed to update database price for {groupid}: {str(e)}")
        return False


def log_price_change(groupid, old_price, new_price, reason):
    """Log the price change to price_change_log table"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO price_change_log (groupid, old_price, new_price, change_date, reason)
            VALUES (%s, %s, %s, CURRENT_DATE, %s)
        """, (groupid, old_price, new_price, reason))

        conn.commit()
        cur.close()
        conn.close()

        return True

    except Exception as e:
        log(f"ERROR: Failed to log price change for {groupid}: {str(e)}")
        return False

def apply_price_changes(approved_changes):
    """Apply all approved price changes"""
    results = {
        'success': 0,
        'failed': 0,
        'details': []
    }
    
    for change in approved_changes:
        groupid = change['groupid']
        current_price = float(change['current_price'])
        new_price = float(change['suggested_price'])
        reason = change['reason']
        change_type = change['change_type']
        
        log(f"Processing {groupid}: £{current_price} -> £{new_price}")
        print(f"Updating {groupid}: £{current_price:.2f} -> £{new_price:.2f}")
        
        success = True

        # Update local database and set shopifychange flag
        if not update_database_price(groupid, new_price):
            success = False

        # Log the change
        if not log_price_change(groupid, current_price, new_price, reason):
            success = False

        if success:
            results['success'] += 1
            results['details'].append(f"SUCCESS {groupid}: £{current_price:.2f} -> £{new_price:.2f}")
            print(f"  SUCCESS")
        else:
            results['failed'] += 1
            results['details'].append(f"FAILED {groupid}: Failed to update")
            print(f"  FAILED")
    
    return results

def main():
    """Main execution function"""
    # Default to simple filename, but allow override
    if len(sys.argv) == 2:
        csv_filename = sys.argv[1]
    else:
        csv_filename = "price_changes.csv"
        print(f"Using default filename: {csv_filename}")
        print("Usage: python apply_price_change.py [csv_filename]")
    
    if not os.path.exists(csv_filename):
        print(f"ERROR: File not found: {csv_filename}")
        return
    
    log("=== BULK PRICE CHANGE APPLICATION STARTED ===")
    print(f"Reading approved changes from: {csv_filename}")

    # Read approved changes
    approved_changes = read_approved_changes(csv_filename)
    
    if not approved_changes:
        print("No approved changes found in CSV file")
        print("Make sure you've entered '1' in the 'approve' column for items you want to change")
        return
    
    print(f"Found {len(approved_changes)} approved changes")
    
    # Confirm before proceeding
    response = input(f"Apply {len(approved_changes)} price changes? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled")
        return
    
    # Apply changes
    print("\nApplying price changes...")
    results = apply_price_changes(approved_changes)

    # If we have successful database updates, run price_update.py to sync to Shopify/Google
    if results['success'] > 0:
        print(f"\nSyncing {results['success']} price changes to Shopify and Google...")
        sync_result = subprocess.run([
            'python', 'price_update.py'
        ], capture_output=True, text=True, timeout=120)

        if sync_result.returncode == 0:
            print("Shopify and Google sync completed successfully")
            log("SUCCESS: Shopify and Google sync completed")
        else:
            print(f"WARNING: Shopify/Google sync had issues: {sync_result.stderr}")
            log(f"WARNING: Shopify/Google sync issues: {sync_result.stderr}")

    # Summary
    print(f"\n=== RESULTS ===")
    print(f"Successful updates: {results['success']}")
    print(f"Failed updates: {results['failed']}")

    if results['details']:
        print(f"\nDetails:")
        for detail in results['details']:
            print(f"  {detail}")
    
    # Create results file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    results_filename = f"price_update_results_{timestamp}.txt"

    with open(results_filename, 'w', encoding='utf-8') as f:
        f.write(f"Bulk Price Update Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Source file: {csv_filename}\n")
        f.write(f"Successful updates: {results['success']}\n")
        f.write(f"Failed updates: {results['failed']}\n\n")
        f.write("Details:\n")
        for detail in results['details']:
            f.write(f"{detail}\n")
    
    print(f"\nResults saved to: {results_filename}")
    
    log(f"Bulk update completed: {results['success']} success, {results['failed']} failed")
    log("=== BULK PRICE CHANGE APPLICATION COMPLETED ===")

if __name__ == "__main__":
    main()
