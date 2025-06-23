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
    """Read CSV file and return approved changes and items to ignore"""
    approved_changes = []
    ignore_items = []

    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                approve_value = row.get('approve', '').strip()

                # Check if approved (user entered '1' in approve column)
                if approve_value == '1':
                    approved_changes.append(row)
                # Check if marked to ignore (user entered 'x' or 'X' in approve column)
                elif approve_value.lower() == 'x':
                    ignore_items.append(row)

        log(f"Loaded {len(approved_changes)} approved changes from {csv_filename}")
        log(f"Loaded {len(ignore_items)} items to mark as ignore auto price changes")
        return approved_changes, ignore_items

    except Exception as e:
        log(f"ERROR: Failed to read CSV file: {str(e)}")
        return [], []

# Removed separate Shopify functions - now using price_update.py for both platforms

def update_ignore_auto_price(groupid):
    """Mark item to ignore auto price changes"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Update skusummary table to ignore auto price changes
        cur.execute("""
            UPDATE skusummary
            SET ignore_auto_price = 1
            WHERE groupid = %s
        """, (groupid,))

        conn.commit()
        cur.close()
        conn.close()

        log(f"SUCCESS: Marked {groupid} to ignore auto price changes")
        return True

    except Exception as e:
        log(f"ERROR: Failed to update ignore_auto_price for {groupid}: {str(e)}")
        return False

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

def process_ignore_items(ignore_items):
    """Process items marked to ignore auto price changes"""
    results = {
        'success': 0,
        'failed': 0,
        'details': []
    }

    for item in ignore_items:
        groupid = item['groupid']

        log(f"Processing ignore flag for {groupid}")
        print(f"Marking {groupid} to ignore auto price changes")

        if update_ignore_auto_price(groupid):
            results['success'] += 1
            results['details'].append(f"SUCCESS {groupid}: Marked to ignore auto price changes")
            print(f"  SUCCESS")
        else:
            results['failed'] += 1
            results['details'].append(f"FAILED {groupid}: Failed to update ignore flag")
            print(f"  FAILED")

    return results

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

    # Read approved changes and ignore items
    approved_changes, ignore_items = read_approved_changes(csv_filename)

    if not approved_changes and not ignore_items:
        print("No approved changes or ignore items found in CSV file")
        print("Make sure you've entered '1' in the 'approve' column for items you want to change")
        print("Or 'x'/'X' in the 'approve' column for items you want to ignore auto price changes")
        return

    if approved_changes:
        print(f"Found {len(approved_changes)} approved price changes")
    if ignore_items:
        print(f"Found {len(ignore_items)} items to mark as ignore auto price changes")

    # Confirm before proceeding
    total_actions = len(approved_changes) + len(ignore_items)
    response = input(f"Process {total_actions} total actions ({len(approved_changes)} price changes, {len(ignore_items)} ignore flags)? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled")
        return
    
    # Process ignore items first
    ignore_results = {'success': 0, 'failed': 0, 'details': []}
    if ignore_items:
        print("\nProcessing ignore auto price change flags...")
        ignore_results = process_ignore_items(ignore_items)

    # Apply price changes
    price_results = {'success': 0, 'failed': 0, 'details': []}
    if approved_changes:
        print("\nApplying price changes...")
        price_results = apply_price_changes(approved_changes)

        # If we have successful database updates, run price_update.py to sync to Shopify/Google
        if price_results['success'] > 0:
            print(f"\nSyncing {price_results['success']} price changes to Shopify and Google...")
            print("Running without timeout - will complete when finished...")

            sync_result = subprocess.run([
                'python', 'price_update.py'
            ], capture_output=True, text=True)

            if sync_result.returncode == 0:
                print("Shopify and Google sync completed successfully")
                log("SUCCESS: Shopify and Google sync completed")
            else:
                print(f"WARNING: Shopify/Google sync had issues:")
                print(f"STDOUT: {sync_result.stdout}")
                print(f"STDERR: {sync_result.stderr}")
                log(f"WARNING: Shopify/Google sync issues: {sync_result.stderr}")

    # Combined summary
    print(f"\n=== RESULTS ===")
    print(f"Price changes - Successful: {price_results['success']}, Failed: {price_results['failed']}")
    print(f"Ignore flags - Successful: {ignore_results['success']}, Failed: {ignore_results['failed']}")

    # Combined details
    all_details = price_results['details'] + ignore_results['details']
    if all_details:
        print(f"\nDetails:")
        for detail in all_details:
            print(f"  {detail}")
    
    # Create results file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    results_filename = f"price_update_results_{timestamp}.txt"

    with open(results_filename, 'w', encoding='utf-8') as f:
        f.write(f"Bulk Price Update Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Source file: {csv_filename}\n")
        f.write(f"Price changes - Successful: {price_results['success']}, Failed: {price_results['failed']}\n")
        f.write(f"Ignore flags - Successful: {ignore_results['success']}, Failed: {ignore_results['failed']}\n\n")
        f.write("Details:\n")
        for detail in all_details:
            f.write(f"{detail}\n")

    print(f"\nResults saved to: {results_filename}")

    total_success = price_results['success'] + ignore_results['success']
    total_failed = price_results['failed'] + ignore_results['failed']
    log(f"Bulk update completed: {total_success} success, {total_failed} failed")
    log("=== BULK PRICE CHANGE APPLICATION COMPLETED ===")

if __name__ == "__main__":
    main()
