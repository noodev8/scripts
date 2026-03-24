"""
SHOPIFY TAG SYNC SCRIPT
========================

PURPOSE:
Syncs the 'lastfew' tag on Shopify products based on skusummary.lastfew (1/0).
Runs a full compare each time — no tracking column needed. DB is the master.

USAGE:
• python update_shopify_tags.py            # Sync lastfew tags to Shopify
• python update_shopify_tags.py --dry-run  # Preview changes without applying

MAIN LOGIC FLOW:
• 1. Query all Shopify-active products and their lastfew status from DB
• 2. Batch-fetch current tags from Shopify via GraphQL
• 3. Compare: add 'lastfew' tag where DB=1 and missing, remove where DB=0 and present
• 4. Update via REST API, preserving all other tags
• 5. Log summary of changes

NOTE:
This script does a full compare of all Shopify products each run (~231 as of March 2026).
If the product count approaches 1,000, switch to a tracking-column approach (like
update_shopify_titles.py uses) to avoid excessive API calls.

NIGHTLY SCHEDULE:
Designed to run nightly via cron, e.g.:
0 3 * * * /apps/scripts/venv/bin/python /apps/scripts/update_shopify_tags.py
"""

import psycopg2
import requests
import sys
import time
import os
from dotenv import load_dotenv
from logging_utils import manage_log_files, create_logger, get_db_config

# --- CONFIGURATION ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in .env file")

TAG_NAME = "lastfew"

# Setup logging
SCRIPT_NAME = "update_shopify_tags"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


def batch_fetch_products(handles, batch_size=25):
    """
    Fetch products by handle via GraphQL in batches.
    Returns dict: {handle: (product_id, [existing_tags])}
    """
    results = {}
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
                    tags
                }
            }
        }
    }
    """

    for i in range(0, len(handles), batch_size):
        batch = handles[i:i + batch_size]
        handle_query = " OR ".join([f"handle:{h}" for h in batch])
        payload = {"query": query, "variables": {"query": handle_query}}

        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 429:
                log("Rate limited, waiting 5 seconds...")
                time.sleep(5)
                r = requests.post(url, json=payload, headers=headers)

            if r.status_code != 200:
                log(f"Batch GraphQL request failed with status {r.status_code}")
                continue

            data = r.json()
            if "errors" in data:
                log(f"GraphQL errors: {data['errors']}")
                continue

            edges = data.get("data", {}).get("products", {}).get("edges", [])
            for edge in edges:
                node = edge["node"]
                handle = node["handle"]
                if handle in batch:
                    product_id = node["id"].split("/")[-1]
                    tags = node.get("tags", [])
                    results[handle] = (product_id, tags)

            time.sleep(1.0)

        except Exception as e:
            log(f"Exception in batch_fetch_products: {str(e)}")
            continue

    return results


def update_shopify_tags(product_id, tags):
    """
    Update a product's tags in Shopify. Tags is a comma-separated string.
    Returns True if successful.
    """
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products/{product_id}.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "product": {
            "id": product_id,
            "tags": tags
        }
    }

    retries = 3
    while retries > 0:
        try:
            r = requests.put(url, json=payload, headers=headers)
            if r.status_code == 200:
                time.sleep(0.5)
                return True
            elif r.status_code == 429:
                log("Rate limited, waiting 5 seconds...")
                time.sleep(5)
                retries -= 1
            else:
                try:
                    error_data = r.json()
                    log(f"Shopify API error {r.status_code}: {error_data}")
                except Exception:
                    log(f"Shopify API error {r.status_code}: {r.text}")
                return False
        except Exception as e:
            log(f"Exception in update_shopify_tags: {str(e)}")
            return False

    log(f"Max retries exceeded for product_id {product_id}")
    return False


def main():
    dry_run = '--dry-run' in sys.argv

    log("=== SHOPIFY TAG SYNC STARTED ===")
    if dry_run:
        log("DRY RUN MODE — no changes will be made")

    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Get all Shopify products and their lastfew status
    cur.execute("""
        SELECT groupid, handle, COALESCE(lastfew, 0) as lastfew
        FROM skusummary
        WHERE shopify = 1
          AND handle IS NOT NULL
          AND TRIM(handle) != ''
        ORDER BY groupid
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        log("No Shopify products found")
        log("=== SHOPIFY TAG SYNC COMPLETED ===")
        return

    log(f"Found {len(rows)} Shopify products to check")

    # Build lookup: handle -> (groupid, wants_tag)
    handle_map = {}
    handles = []
    for groupid, handle, lastfew in rows:
        handle_map[handle] = {'groupid': groupid, 'wants_tag': lastfew == 1}
        handles.append(handle)

    # Fetch current tags from Shopify
    log(f"Fetching current tags from Shopify...")
    product_data = batch_fetch_products(handles)
    log(f"Got tag data for {len(product_data)} of {len(handles)} products")

    added = 0
    removed = 0
    skipped = 0
    failed = 0
    not_found = 0

    for handle, info in handle_map.items():
        groupid = info['groupid']
        wants_tag = info['wants_tag']

        if handle not in product_data:
            log(f"{groupid}: Product handle '{handle}' not found in Shopify — skipping")
            not_found += 1
            continue

        product_id, current_tags = product_data[handle]
        has_tag = TAG_NAME in current_tags

        if wants_tag and has_tag:
            skipped += 1
            continue
        elif not wants_tag and not has_tag:
            skipped += 1
            continue
        elif wants_tag and not has_tag:
            # Add the tag
            new_tags = ", ".join(current_tags + [TAG_NAME])
            action = "ADD"
        else:
            # Remove the tag
            new_tags = ", ".join([t for t in current_tags if t != TAG_NAME])
            action = "REMOVE"

        if dry_run:
            log(f"{groupid}: [DRY RUN] Would {action} '{TAG_NAME}' tag (product_id: {product_id})")
            if action == "ADD":
                added += 1
            else:
                removed += 1
            continue

        log(f"{groupid}: {action} '{TAG_NAME}' tag (product_id: {product_id})")
        success = update_shopify_tags(product_id, new_tags)

        if success:
            if action == "ADD":
                added += 1
            else:
                removed += 1
        else:
            failed += 1
            log(f"{groupid}: Failed to {action} tag")

        # Rate limiting
        if (added + removed + failed) % 10 == 0:
            time.sleep(2.0)

    log(f"Results: {added} added, {removed} removed, {skipped} already correct, {not_found} not found in Shopify, {failed} failed")
    if dry_run:
        log("DRY RUN — no changes were made")
    log("=== SHOPIFY TAG SYNC COMPLETED ===")


if __name__ == "__main__":
    main()
