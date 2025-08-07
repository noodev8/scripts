"""
SHOPIFY TITLE SYNC SCRIPT
=========================

PURPOSE:
Updates Shopify product titles from the database title table, only processing titles
that have been changed since the last sync (last_shopify_sync IS NULL).

USAGE:
• python update_shopify_titles.py           # Update only changed titles (NULL sync)
• python update_shopify_titles.py --force   # Update ALL titles (ignore sync status)

MAIN LOGIC FLOW:
• 1. DATABASE FILTERING: Only processes items where skusummary.shopify = 1
• 2. CHANGE DETECTION: Only updates titles where last_shopify_sync IS NULL
• 3. BATCH PROCESSING: Uses GraphQL batch API to find Shopify product IDs
• 4. TITLE COMPARISON: Only updates if database title ≠ current Shopify title
• 5. API UPDATES: Uses Shopify Products API to update titles
• 6. TRACKING UPDATE: Sets last_shopify_sync timestamp after successful update

WEEKLY SCHEDULE:
Designed to run weekly on Tuesday 4 AM via cron:
0 4 * * 2 /apps/scripts/venv/bin/python /apps/scripts/update_shopify_titles.py

MANUAL USAGE:
• To mark specific title for update: UPDATE title SET last_shopify_sync = NULL WHERE groupid = 'ABC123';
• To refresh all titles: UPDATE title SET last_shopify_sync = NULL;
"""

import psycopg2
import requests
import sys
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from logging_utils import manage_log_files, create_logger, get_db_config

# --- CONFIGURATION ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

# Validate that the access token was loaded
if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in .env file")

# Setup logging
SCRIPT_NAME = "update_shopify_titles"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


def batch_search_products_by_handle(handles, batch_size=25):
    """
    Search for multiple products by handle using Shopify's GraphQL API in batches.
    Returns dict: {handle: (product_id, current_title)}
    """
    results = {}

    # Process handles in batches to respect API limits
    for i in range(0, len(handles), batch_size):
        batch_handles = handles[i:i + batch_size]

        # Build query string for multiple handles
        handle_queries = " OR ".join([f"handle:{handle}" for handle in batch_handles])

        url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
        headers = {
            "X-Shopify-Access-Token": ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

        query = """
        query($query: String!) {
            products(first: 100, query: $query) {
                edges {
                    node {
                        id
                        handle
                        title
                    }
                }
            }
        }
        """

        variables = {"query": handle_queries}
        payload = {"query": query, "variables": variables}

        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 429:  # Rate limited
                log("Rate limited, waiting 5 seconds...")
                time.sleep(5)
                r = requests.post(url, json=payload, headers=headers)

            if r.status_code != 200:
                log(f"❌ Batch GraphQL request failed with status {r.status_code}")
                continue

            data = r.json()

            # Check for GraphQL errors
            if "errors" in data:
                log(f"❌ GraphQL errors in batch request: {data['errors']}")
                continue

            edges = data.get("data", {}).get("products", {}).get("edges", [])

            for edge in edges:
                product = edge["node"]
                handle = product["handle"]

                if handle in batch_handles:  # Only process handles we asked for
                    # Extract ID (remove gid://shopify/ prefix)
                    product_id = product["id"].split("/")[-1]
                    current_title = product["title"]

                    results[handle] = (product_id, current_title)

            # Delay between batches
            time.sleep(1.0)

        except Exception as e:
            log(f"❌ Exception in batch_search_products_by_handle: {str(e)}")
            continue

    return results


def update_shopify_product_title(product_id, new_title):
    """
    Update a product's title in Shopify using the REST API.
    Returns True if successful, False otherwise.
    """
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products/{product_id}.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "product": {
            "id": product_id,
            "title": new_title
        }
    }

    retries = 3
    while retries > 0:
        try:
            r = requests.put(url, json=payload, headers=headers)
            if r.status_code == 200:
                # Small delay after successful update
                time.sleep(0.5)
                return True
            elif r.status_code == 429:
                log("Rate limited, waiting 5 seconds...")
                time.sleep(5)
                retries -= 1
            else:
                # Log the specific error for debugging
                try:
                    error_data = r.json()
                    log(f"❌ Shopify API error {r.status_code}: {error_data}")
                except:
                    log(f"❌ Shopify API error {r.status_code}: {r.text}")
                return False
        except Exception as e:
            log(f"❌ Exception in update_shopify_product_title: {str(e)}")
            return False

    log(f"❌ Max retries exceeded for product_id {product_id}")
    return False


def verify_title_update(product_id, expected_title):
    """
    Verify that the title update was successful by fetching the current title.
    Returns True if title matches, False otherwise.
    """
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products/{product_id}.json"
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    
    try:
        time.sleep(1.0)  # Give Shopify time to process the update
        r = requests.get(url, headers=headers)
        
        if r.status_code == 429:  # Rate limited
            time.sleep(5)
            r = requests.get(url, headers=headers)
            
        if r.status_code == 200:
            product_data = r.json().get("product", {})
            current_title = product_data.get("title", "")
            return current_title == expected_title
        else:
            log(f"❌ Failed to verify title update for product {product_id}: HTTP {r.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ Exception verifying title update: {str(e)}")
        return False


def main():
    force_update = '--force' in sys.argv

    log("=== SHOPIFY TITLE SYNC STARTED ===")
    if force_update:
        log("Force mode: Updating ALL titles regardless of sync status")
    else:
        log("Normal mode: Updating only changed titles (last_shopify_sync IS NULL)")

    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Query for titles that need updating
    if force_update:
        query = """
            SELECT ss.groupid, ss.handle, t.shopifytitle
            FROM skusummary ss
            JOIN title t ON ss.groupid = t.groupid
            WHERE ss.shopify = 1 
              AND ss.handle IS NOT NULL 
              AND TRIM(ss.handle) != ''
              AND t.shopifytitle IS NOT NULL 
              AND TRIM(t.shopifytitle) != ''
            ORDER BY ss.groupid
        """
    else:
        query = """
            SELECT ss.groupid, ss.handle, t.shopifytitle
            FROM skusummary ss
            JOIN title t ON ss.groupid = t.groupid
            WHERE ss.shopify = 1 
              AND ss.handle IS NOT NULL 
              AND TRIM(ss.handle) != ''
              AND t.shopifytitle IS NOT NULL 
              AND TRIM(t.shopifytitle) != ''
              AND t.last_shopify_sync IS NULL
            ORDER BY ss.groupid
        """

    cur.execute(query)
    rows = cur.fetchall()

    if not rows:
        log("No titles found that need updating")
        log("=== SHOPIFY TITLE SYNC COMPLETED ===")
        cur.close()
        conn.close()
        return

    log(f"Found {len(rows)} titles that need updating")

    # Extract handles for batch lookup
    handle_to_data = {}
    handles = []
    
    for groupid, handle, shopifytitle in rows:
        handle_to_data[handle] = {
            'groupid': groupid,
            'shopifytitle': shopifytitle
        }
        handles.append(handle)

    # Get product data from Shopify in batches
    log(f"Fetching product information for {len(handles)} products...")
    product_data = batch_search_products_by_handle(handles)
    log(f"Found product information for {len(product_data)} out of {len(handles)} products")

    updated_count = 0
    failed_count = 0
    skipped_count = 0
    processed_count = 0

    for handle, handle_data in handle_to_data.items():
        processed_count += 1
        groupid = handle_data['groupid']
        new_title = handle_data['shopifytitle']

        # Progress logging every 50 items
        if processed_count % 50 == 0:
            log(f"Progress: {processed_count}/{len(handle_to_data)} processed, {updated_count} updated, {skipped_count} skipped, {failed_count} failed")

        # Check if we found the product in Shopify
        if handle not in product_data:
            log(f"{groupid}: ⚠️  Product handle '{handle}' not found in Shopify - skipping")
            skipped_count += 1
            continue

        product_id, current_title = product_data[handle]

        # Only update if titles are different
        if current_title == new_title:
            log(f"{groupid}: Title already matches - no update needed")
            # Still update the tracking timestamp since we checked it
            try:
                cur.execute(
                    "UPDATE title SET last_shopify_sync = CURRENT_TIMESTAMP WHERE groupid = %s",
                    (groupid,)
                )
                conn.commit()
            except Exception as e:
                log(f"❌ Failed to update tracking timestamp for {groupid}: {str(e)}")
            
            skipped_count += 1
            continue

        log(f"{groupid}: Updating title from '{current_title}' → '{new_title}' (product_id: {product_id})")
        
        # Update the title in Shopify
        success = update_shopify_product_title(product_id, new_title)
        
        if success:
            # Verify the update took effect
            if verify_title_update(product_id, new_title):
                updated_count += 1
                log(f"{groupid}: ✅ Title updated successfully")
                
                # Update tracking timestamp in database
                try:
                    cur.execute(
                        "UPDATE title SET last_shopify_sync = CURRENT_TIMESTAMP WHERE groupid = %s",
                        (groupid,)
                    )
                    conn.commit()
                except Exception as e:
                    log(f"❌ Failed to update tracking timestamp for {groupid}: {str(e)}")
            else:
                failed_count += 1
                log(f"{groupid}: ❌ Title update verification failed")
        else:
            failed_count += 1
            log(f"{groupid}: ❌ Failed to update title")

        # Rate limiting: pause every 10 updates
        if processed_count % 10 == 0:
            time.sleep(2.0)

    cur.close()
    conn.close()

    # Final summary
    log(f"Processing complete: {updated_count} updated, {skipped_count} skipped, {failed_count} failed")
    log(f"Mode: {'force' if force_update else 'normal'}")
    log("=== SHOPIFY TITLE SYNC COMPLETED ===")


if __name__ == "__main__":
    main()