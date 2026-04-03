#!/usr/bin/env python3
"""
Update amzfeed.amzprice in the database from a price upload file.
Reads AMZ-Price-Upload.txt and updates the corresponding rows in amzfeed.

Usage: python amz-price/update_amz_price.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from logging_utils import get_db_config

UPLOAD_FILE = os.path.join(os.path.expanduser('~'), 'Downloads', 'AMZ-Price-Upload.txt')

def main():
    if not os.path.exists(UPLOAD_FILE):
        print(f"No upload file found: {UPLOAD_FILE}")
        return

    # Read price changes from upload file
    changes = []
    with open(UPLOAD_FILE, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if i == 0 or not line:  # skip header and blank lines
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                sku = parts[0]
                price = parts[1]
                changes.append((sku, price))

    if not changes:
        print("No price changes found in upload file.")
        return

    # Connect and update
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    print(f"Updating {len(changes)} price(s) in amzfeed...")
    for sku, price in changes:
        # Get current price and code before updating
        cur.execute("SELECT code, amzprice FROM amzfeed WHERE sku = %s", (sku,))
        row = cur.fetchone()
        if not row:
            print(f"  {sku} -> {price} (WARNING: no matching SKU found)")
            continue

        code, old_price = row
        cur.execute("UPDATE amzfeed SET amzprice = %s WHERE sku = %s", (price, sku))
        print(f"  {sku} -> {price}")

        # Log the change
        if old_price and str(old_price).strip() != str(price).strip():
            cur.execute(
                "INSERT INTO amz_price_log (code, old_price, new_price) VALUES (%s, %s, %s)",
                (code, old_price, price)
            )

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")

if __name__ == '__main__':
    main()
