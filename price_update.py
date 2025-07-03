# --- USAGE ---
# python price_update.py                    # Changed only (default), Google updates enabled
# python price_update.py full               # Force full update, Google updates enabled
# python price_update.py --no-google        # Changed only, Google updates disabled
# python price_update.py full --no-google   # Force full update, Google updates disabled
# python price_update.py --help             # Show usage help
#

import psycopg2
import requests
import sys
import time
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from logging_utils import manage_log_files, create_logger, get_db_config

# --- SHOPIFY CONFIGURATION ---
# Load environment variables from .env
load_dotenv('.env')

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
LOG_RETENTION = 7  # days

# Validate that the access token was loaded
if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in .env file")

# --- GOOGLE CONFIGURATION ---
GOOGLE_SERVICE_ACCOUNT_FILE = 'merchant-feed-api-462809-23c712978791.json'
GOOGLE_MERCHANT_ID = '124941872'
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/content']

# Global Google service instance
google_service = None

# Setup logging
SCRIPT_NAME = "price_update"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


def initialize_google_service():
    """Initialize Google Content API service"""
    global google_service
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(script_dir, GOOGLE_SERVICE_ACCOUNT_FILE)

        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=GOOGLE_SCOPES
        )
        google_service = build('content', 'v2.1', credentials=credentials)
        return True
    except Exception as e:
        log(f"Google API initialization failed: {str(e)}")
        return False





def batch_search_variants_by_sku(skus, batch_size=50):
    """
    Search for multiple variants by SKU using Shopify's GraphQL API in batches.
    Returns dict: {sku: (variant_id, current_price, product_title)}
    """
    results = {}

    # Process SKUs in batches to respect API limits
    for i in range(0, len(skus), batch_size):
        batch_skus = skus[i:i + batch_size]

        # Build query string for multiple SKUs
        sku_queries = " OR ".join([f"sku:{sku}" for sku in batch_skus])

        url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
        headers = {
            "X-Shopify-Access-Token": ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

        query = """
        query($query: String!) {
            productVariants(first: 250, query: $query) {
                edges {
                    node {
                        id
                        sku
                        price
                        product {
                            title
                            id
                        }
                    }
                }
            }
        }
        """

        variables = {"query": sku_queries}
        payload = {"query": query, "variables": variables}

        try:
            batch_call_start = datetime.now()
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 429:  # Rate limited
                log(f"Rate limited on batch {batch_num}, waiting 5 seconds...")
                time.sleep(5)
                r = requests.post(url, json=payload, headers=headers)

            batch_call_end = datetime.now()
            call_duration = (batch_call_end - batch_call_start).total_seconds()

            if r.status_code != 200:
                log(f"Batch {batch_num} GraphQL request failed with status {r.status_code} (took {call_duration:.2f}s)")
                continue
            else:
                log(f"Batch {batch_num} completed successfully (took {call_duration:.2f}s)")

            data = r.json()

            # Check for GraphQL errors
            if "errors" in data:
                log(f"❌ GraphQL errors in batch request: {data['errors']}")
                continue

            edges = data.get("data", {}).get("productVariants", {}).get("edges", [])

            for edge in edges:
                variant = edge["node"]
                sku = variant["sku"]

                if sku in batch_skus:  # Only process SKUs we asked for
                    # Extract IDs (remove gid://shopify/ prefix)
                    variant_id = variant["id"].split("/")[-1]
                    current_price = variant["price"]
                    product_title = variant["product"]["title"]

                    results[sku] = (variant_id, current_price, product_title)

            # Delay between batches
            time.sleep(0.5)

        except Exception as e:
            log(f"Exception in batch_search_variants_by_sku: {str(e)}")
            continue

    return results


def search_variant_by_sku(sku):
    """
    Search for a variant by SKU using Shopify's GraphQL API.
    Returns variant_id, current_price, and product_title for verification.
    """
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    query = """
    query($sku: String!) {
        productVariants(first: 1, query: $sku) {
            edges {
                node {
                    id
                    sku
                    price
                    product {
                        title
                        id
                    }
                }
            }
        }
    }
    """

    variables = {"sku": f"sku:{sku}"}
    payload = {"query": query, "variables": variables}

    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 429:  # Rate limited
            time.sleep(5)
            r = requests.post(url, json=payload, headers=headers)

        if r.status_code != 200:
            return None, None, None

        data = r.json()

        # Check for GraphQL errors
        if "errors" in data:
            log(f"GraphQL error for SKU {sku}: {data['errors']}")
            return None, None, None

        edges = data.get("data", {}).get("productVariants", {}).get("edges", [])
        if not edges:
            return None, None, None

        variant = edges[0]["node"]

        # Extract data
        variant_id = variant["id"].split("/")[-1]
        current_price = variant["price"]
        product_title = variant["product"]["title"]

        # Small delay between API calls
        time.sleep(0.1)

        return variant_id, current_price, product_title

    except Exception as e:
        log(f"Exception in search_variant_by_sku for {sku}: {str(e)}")
        return None, None, None


def get_variant_info_by_sku(code):
    """
    Get variant info by searching for the SKU only.
    This ensures we always get the current, correct variant ID and price.
    If SKU is not found in Shopify, returns None to prevent incorrect updates.
    """
    # Search by the exact code (SKU) - this is the ONLY method we use
    variant_id, current_price, product_title = search_variant_by_sku(code)

    if variant_id and current_price is not None:
        return variant_id, current_price, product_title

    # If not found, do NOT use any fallback - safety first
    return None, None, None


def get_current_shopify_price(variant_id):
    """Legacy function - kept for compatibility but should use get_variant_info_by_sku instead"""
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/variants/{variant_id}.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 429:  # Rate limited
            time.sleep(5)
            r = requests.get(url, headers=headers)
        if r.status_code == 200:
            # Small delay between API calls
            time.sleep(0.1)
            return r.json()["variant"]["price"]
        return None
    except Exception:
        return None


def update_variant_links_in_database(variant_updates, cur, conn):
    """
    Update the variantlink field in the database with current variant IDs.
    variant_updates: dict {code: variant_id}
    """
    if not variant_updates:
        return

    updated_count = 0
    for code, variant_id in variant_updates.items():
        try:
            cur.execute(
                "UPDATE skumap SET variantlink = %s WHERE code = %s",
                (f"{variant_id}V", code)
            )
            if cur.rowcount > 0:
                updated_count += 1
        except Exception as e:
            log(f"Failed to update variantlink for {code}: {str(e)}")

    if updated_count > 0:
        conn.commit()
        log(f"Updated {updated_count} variant links in database")


def update_variant_price(variant_id, new_price):
    if not variant_id:
        return False

    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/variants/{variant_id}.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "variant": {
            "id": variant_id,
            "price": new_price
        }
    }

    retries = 5
    while retries > 0:
        try:
            response = requests.put(url, json=payload, headers=headers)
            if response.status_code == 200:
                # Small delay after successful update
                time.sleep(0.1)
                return True
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "5"))
                time.sleep(max(retry_after, 5))  # Wait at least 5 seconds
                retries -= 1
            else:
                return f"Failed — HTTP {response.status_code}"
        except Exception as e:
            return f"Exception — {str(e)}"

    return "Rate limit exceeded"


def update_google_price(google_id, new_price):
    """Update Google Merchant Center product price"""
    global google_service

    if not google_service:
        return "Google service not initialized"

    if not google_id:
        return "No Google ID provided"

    try:
        request_body = {
            "price": {
                "value": str(new_price),
                "currency": "GBP"
            },
            "salePrice": {
                "value": str(new_price),
                "currency": "GBP"
            }
        }

        response = google_service.products().update(
            merchantId=GOOGLE_MERCHANT_ID,
            productId= 'online:en:GB:' + google_id,
            body=request_body
        ).execute()

        # Small delay after Google API call
        time.sleep(0.1)
        return True

    except Exception as e:
        # Add delay even for errors to avoid overwhelming the API
        time.sleep(0.2)
        return f"Google API error: {str(e)}"

def log_price_change_to_db(groupid, old_price, new_price, reason="PRICE_UPDATE_SCRIPT"):
    """Log price change to database for tracking"""
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Insert into price_change_log table
        cur.execute("""
            INSERT INTO price_change_log (groupid, old_price, new_price, reason, reviewed_by, change_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (groupid, old_price, new_price, reason, "PRICE_UPDATE", datetime.now().date()))

        # conn.commit()
        # cur.close()
        # conn.close()

        return True

    except Exception as e:
        log(f"ERROR: Failed to log price change to database for {groupid}: {str(e)}")
        return False


def show_usage():
    print("Usage:")
    print("  python price_update.py                    # Only update changed, Google enabled")
    print("  python price_update.py full               # Force update all, Google enabled")
    print("  python price_update.py --no-google        # Only update changed, Google disabled")
    print("  python price_update.py full --no-google   # Force update all, Google disabled")
    print("  python price_update.py --help             # Show help")
    print("")
    print("Google updates: Uses googleid from skumap table, updates price only (no availability), currency always GBP")


def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--help", "-h"):
        show_usage()
        return

    # Record start time
    start_time = datetime.now()

    # Parse command line arguments
    mode = "changed"
    google_updates_enabled = True

    for arg in sys.argv[1:]:
        if arg.lower() == "full":
            mode = "full"
        elif arg.lower() == "--no-google":
            google_updates_enabled = False

    # Log start of operation
    log(f"Starting price update - mode: {mode}, Google updates: {'enabled' if google_updates_enabled else 'disabled'}")

    # Initialize Google service if enabled
    google_initialized = False
    if google_updates_enabled:
        google_initialized = initialize_google_service()
        if not google_initialized:
            log("Warning: Google updates disabled due to initialization failure")
            google_updates_enabled = False

    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    if mode == "full":
        cur.execute("SELECT groupid, shopifyprice FROM skusummary WHERE shopify = 1")
    else:
        cur.execute("SELECT groupid, shopifyprice FROM skusummary WHERE shopify = 1 AND shopifychange = 1")

    group_rows = cur.fetchall()
    total_processed = 0
    shopify_updates = 0
    google_updates = 0
    google_failures = 0
    processed_groups = 0
    total_groups = len(group_rows)
    variant_updates = {}  # Track variant IDs that need database updates

    # Collect all SKUs for batch variant lookup
    all_codes = []
    for groupid, shopifyprice in group_rows:
        cur.execute("SELECT code FROM skumap WHERE groupid = %s", (groupid,))
        codes = [row[0] for row in cur.fetchall()]
        all_codes.extend(codes)

    # Get all variant data in batches to minimize API calls
    log(f"Fetching variant information for {len(all_codes)} SKUs across {total_groups} product groups...")
    batch_start_time = datetime.now()
    variant_data = batch_search_variants_by_sku(all_codes)
    batch_end_time = datetime.now()
    batch_duration = (batch_end_time - batch_start_time).total_seconds()
    log(f"Found variant information for {len(variant_data)} out of {len(all_codes)} SKUs in {batch_duration:.1f} seconds")

    # Log start details for full mode
    if mode == "full":
        log(f"Starting FULL price sync for {total_groups} product groups...")

    # Start timing the price update phase
    price_update_start = datetime.now()
    log(f"Starting price update phase at {price_update_start.strftime('%H:%M:%S')}")

    for groupid, shopifyprice in group_rows:
        processed_groups += 1
        cur.execute("SELECT code, variantlink, googleid FROM skumap WHERE groupid = %s", (groupid,))
        variants = cur.fetchall()

        success = True
        group_price_changed = False  # Track if any variant in this group had a price change
        first_price_change = None   # Store details of first price change for logging

        for code, variantlink, googleid in variants:
            # Check if we have variant data from the batch lookup
            if code in variant_data:
                variant_id, current_price, product_title = variant_data[code]

                # Check if we need to update the stored variant link
                stored_variant = variantlink.rstrip("V").strip() if variantlink else ""
                if stored_variant != variant_id:
                    variant_updates[code] = variant_id

            else:
                # Try individual lookup if not found in batch - SKU search only, no fallback
                variant_id, current_price, product_title = get_variant_info_by_sku(code)
                if not variant_id:
                    log(f"{code}: ⚠️  SKU not found in Shopify - skipping price update for safety")
                    success = False
                    continue

                # Track this variant for database update
                variant_updates[code] = variant_id

            # Compare prices as floats to avoid string formatting differences (e.g., "80.00" vs "80")
            if float(current_price) != float(shopifyprice):
                # Update Shopify price
                shopify_start = datetime.now()
                result = update_variant_price(variant_id, shopifyprice)
                shopify_end = datetime.now()
                shopify_duration = (shopify_end - shopify_start).total_seconds()

                if result is True:
                    shopify_updates += 1
                    # Log detailed price change information for both modes
                    price_change_msg = f"{code}: PRICE CHANGED - '{product_title}' from £{current_price} -> £{shopifyprice} (variant_id: {variant_id}) [Shopify: {shopify_duration:.2f}s]"
                    log(price_change_msg)

                    # Track that this group had a price change (for database logging)
                    if not group_price_changed:
                        group_price_changed = True
                        first_price_change = (current_price, shopifyprice)

                    # Update Google price if enabled and googleid exists
                    if google_updates_enabled and googleid:
                        google_start = datetime.now()
                        google_result = update_google_price(googleid, shopifyprice)
                        google_end = datetime.now()
                        google_duration = (google_end - google_start).total_seconds()

                        if google_result is True:
                            google_updates += 1
                            log(f"{code}: Google price updated to £{shopifyprice} [Google: {google_duration:.2f}s]")
                        else:
                            google_failures += 1
                            log(f"{code}: Google update failed - {google_result} [Google: {google_duration:.2f}s]")
                else:
                    log(f"{code}: Shopify update failed - {result} [Shopify: {shopify_duration:.2f}s]")
                    success = False

            total_processed += 1

            # Rate limiting: 2 second pause every 30 API calls to stay under 40/second limit
            if total_processed % 30 == 0:
                log(f"Rate limiting pause after {total_processed} API calls...")
                time.sleep(2)

        # Log price change to database once per group (not per variant)
        if group_price_changed and first_price_change:
            old_price, new_price = first_price_change
            log_price_change_to_db(groupid, old_price, new_price, f"PRICE_UPDATE_{mode.upper()}")

        # Progress logging for full mode every 50 groups
        if mode == "full" and processed_groups % 50 == 0:
            log(f"Progress: {processed_groups}/{total_groups} groups processed, {total_processed} variants checked, {shopify_updates} Shopify updates, {google_updates} Google updates")

        if mode == "changed" and success:
            cur.execute("UPDATE skusummary SET shopifychange = 0 WHERE groupid = %s", (groupid,))

    # Update variant links in database if we found any discrepancies
    update_variant_links_in_database(variant_updates, cur, conn)

    conn.commit()
    cur.close()
    conn.close()

    # Calculate duration and timing breakdown
    end_time = datetime.now()
    total_duration = end_time - start_time
    batch_duration_total = batch_duration if 'batch_duration' in locals() else 0
    price_update_duration = (end_time - price_update_start).total_seconds() if 'price_update_start' in locals() else 0

    duration_str = str(total_duration).split('.')[0]  # Remove microseconds

    # Final summary log with timing breakdown
    summary = f"Sync complete - mode: {mode}, groups: {len(group_rows)}, total variants: {total_processed}"
    summary += f", Shopify price changes: {shopify_updates}"
    if google_updates_enabled:
        summary += f", Google updates: {google_updates}, Google failures: {google_failures}"
    else:
        summary += ", Google updates: disabled"
    summary += f", Total duration: {duration_str}"

    log(summary)
    log(f"TIMING BREAKDOWN:")
    log(f"  - Batch variant lookup: {batch_duration_total:.1f}s")
    log(f"  - Price update phase: {price_update_duration:.1f}s")
    log(f"  - Total time: {total_duration.total_seconds():.1f}s")

    # Additional summary for price changes
    if shopify_updates > 0:
        log(f"SUMMARY: {shopify_updates} price changes were made during this sync")
    else:
        log("SUMMARY: No price changes were needed during this sync")


if __name__ == "__main__":
    main()
