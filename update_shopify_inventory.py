"""
SHOPIFY INVENTORY SYNC SCRIPT
=============================

PURPOSE:
Synchronizes inventory levels between our database and Shopify, ensuring accurate stock display
while preventing overselling due to timing gaps in order processing.

USAGE:
• python update_shopify_inventory.py             # Sync all Shopify items in the database
• python update_shopify_inventory.py M404A-10    # Sync only the item with code 'M404A-10'

MAIN LOGIC FLOW:
• 1. DATABASE FILTERING: Only processes items where skusummary.shopify = 1
• 2. STOCK CALCULATION: Calculates total stock from 3 sources (priority order):
    - localstock table (qty > 0, deleted = 0, ordernum = '#FREE')
    - ukdstock table (stock > 0)
    - amzfeed table (amzlive > 0)
• 3. UNFULFILLED ORDERS CHECK: Subtracts Shopify orders not yet in orderstatus table
    - Prevents overselling during order processing gaps
    - Handles 9pm-3am scenario where orders exist but aren't processed yet
• 4. STOCK CAPPING: Limits displayed stock to maximum of 5 items
    - Saves API calls (12→10 changes become 5→5, no update needed)
    - Safe for 3x daily runs (max 15 items could sell between syncs)
• 5. VARIANT LOOKUP: Uses GraphQL batch API to find Shopify variant IDs by SKU
    - Batch processing for efficiency (50 SKUs per API call)
    - Falls back to individual lookup if needed
    - Updates database variantlink if discrepancies found
• 6. SHOPIFY COMPARISON: Only updates if calculated stock ≠ current Shopify stock
    - Prevents unnecessary API calls
    - Logs all changes with detailed reasoning
• 7. RATE LIMITING: Conservative API usage to respect Shopify limits
    - 0.1s delays between API calls
    - 5s waits for rate limit errors
    - 1.5s pause every 20 processed items

ERROR HANDLING:
• Graceful degradation if unfulfilled orders API fails (continues without check)
• Comprehensive logging of all operations and failures
• Verification of inventory updates to ensure they took effect
• Automatic retry logic for rate-limited requests

PERFORMANCE OPTIMIZATIONS:
• Bulk database queries for stock calculation (1 query vs 3000+)
• Batch GraphQL API calls for variant lookup
• Minimal API calls (only when stock differs)
• Progress logging every 100 items for monitoring

SAFETY FEATURES:
• SKU-only variant lookup (no fallback to prevent wrong updates)
• Stock verification after updates
• Negative stock prevention
• Conservative rate limiting
• Detailed audit trail in logs
"""

import psycopg2
import requests
import sys
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from logging_utils import manage_log_files, create_logger

# --- CONFIGURATION ---
# Load environment variables from shopify_api.env
load_dotenv('shopify_api.env')

DB_CONFIG = {
    "host": "77.68.13.150",
    "port": 5432,
    "user": "brookfield_prod_user",
    "password": "prodpw",
    "dbname": "brookfield_prod"
}

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
LOCATION_ID = "64140443707"

# Validate that the access token was loaded
if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in shopify_api.env file")

# Setup logging
SCRIPT_NAME = "update_shopify_inventory"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


# Old logging functions removed - handled by shared logging system


def batch_search_variants_by_sku(skus, batch_size=50):
    """
    Search for multiple variants by SKU using Shopify's GraphQL API in batches.
    Returns dict: {sku: (variant_id, inventory_item_id, product_title)}
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
                        inventoryItem {
                            id
                        }
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
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 429:  # Rate limited
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

            edges = data.get("data", {}).get("productVariants", {}).get("edges", [])

            for edge in edges:
                variant = edge["node"]
                sku = variant["sku"]

                if sku in batch_skus:  # Only process SKUs we asked for
                    # Extract IDs (remove gid://shopify/ prefix)
                    variant_id = variant["id"].split("/")[-1]
                    inventory_item_id = variant["inventoryItem"]["id"].split("/")[-1]
                    product_title = variant["product"]["title"]

                    results[sku] = (variant_id, inventory_item_id, product_title)

            # Delay between batches
            time.sleep(0.5)

        except Exception as e:
            log(f"❌ Exception in batch_search_variants_by_sku: {str(e)}")
            continue

    return results


def search_variant_by_sku(sku):
    """
    Search for a variant by SKU using Shopify's GraphQL API.
    Returns variant_id, inventory_item_id, and product_title for verification.
    """
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    # GraphQL query to find variant by SKU
    query = """
    query($sku: String!) {
        productVariants(first: 1, query: $sku) {
            edges {
                node {
                    id
                    sku
                    inventoryItem {
                        id
                    }
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

        # Extract IDs (remove gid://shopify/ prefix)
        variant_id = variant["id"].split("/")[-1]
        inventory_item_id = variant["inventoryItem"]["id"].split("/")[-1]
        product_title = variant["product"]["title"]

        # Small delay between API calls
        time.sleep(0.1)

        return variant_id, inventory_item_id, product_title

    except Exception as e:
        log(f"Exception in search_variant_by_sku for {sku}: {str(e)}")
        return None, None, None


def get_variant_and_inventory_item(code, cur):
    """
    Get variant and inventory item info by searching for the SKU only.
    This ensures we always get the current, correct variant ID.
    If SKU is not found in Shopify, returns None to prevent incorrect updates.
    """
    # Search by the exact code (SKU) - this is the ONLY method we use
    variant_id, inventory_item_id, product_title = search_variant_by_sku(code)

    if variant_id and inventory_item_id:
        return variant_id, inventory_item_id, product_title

    # If not found, do NOT use any fallback - safety first
    return None, None, None


def get_current_shopify_stock(inventory_item_id):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/inventory_levels.json"
    params = {
        "inventory_item_ids": inventory_item_id,
        "location_ids": LOCATION_ID
    }
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    try:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 429:  # Rate limited
            time.sleep(5)
            r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            return None
        levels = r.json().get("inventory_levels", [])
        # Small delay between API calls
        time.sleep(0.1)
        return levels[0]["available"] if levels else None
    except Exception:
        return None


def set_shopify_inventory(inventory_item_id, quantity):
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/inventory_levels/set.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "location_id": LOCATION_ID,
        "inventory_item_id": inventory_item_id,
        "available": quantity
    }

    retries = 5
    while retries > 0:
        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 200:
                # Small delay after successful update
                time.sleep(0.2)

                # Verify the update actually took effect
                time.sleep(0.5)  # Give Shopify time to process
                actual_qty = get_current_shopify_stock(inventory_item_id)
                if actual_qty == quantity:
                    return True
                else:
                    log(f"⚠️  Update verification failed: expected {quantity}, got {actual_qty} for inventory_item_id {inventory_item_id}")
                    return False
            elif r.status_code == 429:
                time.sleep(5)  # Longer wait for rate limit
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
            log(f"❌ Exception in set_shopify_inventory: {str(e)}")
            return False

    log(f"❌ Max retries exceeded for inventory_item_id {inventory_item_id}")
    return False


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
            log(f"❌ Failed to update variantlink for {code}: {str(e)}")

    if updated_count > 0:
        conn.commit()
        log(f"📝 Updated {updated_count} variant links in database")


def calculate_total_stock_bulk(codes, cur):
    """
    Calculate stock for multiple codes in a single optimized query.
    Returns dict: {code: total_stock}
    """
    if not codes:
        return {}

    # Create placeholders for the IN clause
    placeholders = ','.join(['%s'] * len(codes))

    cur.execute(f"""
        WITH stock_data AS (
            SELECT
                sm.code,
                COALESCE(SUM(ls.qty), 0) as local_stock,
                COALESCE(MAX(uk.stock), 0) as ukd_stock,
                COALESCE(MAX(af.amzlive), 0) as amz_stock
            FROM skumap sm
            LEFT JOIN localstock ls ON ls.code = sm.code
                AND ls.ordernum = '#FREE' AND ls.deleted = 0
            LEFT JOIN ukdstock uk ON uk.code = sm.code
            LEFT JOIN amzfeed af ON af.code = sm.code
            WHERE sm.code IN ({placeholders})
            GROUP BY sm.code
        )
        SELECT
            code,
            (local_stock + ukd_stock + amz_stock) as total_stock
        FROM stock_data
    """, codes)

    return {row[0]: row[1] for row in cur.fetchall()}


def calculate_total_stock(code, cur):
    """Legacy function for single code - uses bulk function"""
    result = calculate_total_stock_bulk([code], cur)
    return result.get(code, 0)


def get_unfulfilled_shopify_orders():
    """
    Get unfulfilled orders from Shopify and return dict of {sku: total_qty}
    Only includes orders that are not yet in our orderstatus table
    Returns empty dict if API access is denied or fails
    """
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/orders.json"
    params = {
        "status": "open",
        "fulfillment_status": "unfulfilled",
        "limit": 250  # Max per page
    }
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}

    try:
        # Get unfulfilled orders from Shopify
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 429:  # Rate limited
            time.sleep(5)
            r = requests.get(url, headers=headers, params=params)

        if r.status_code == 403:
            log("⚠️  Orders API access denied (HTTP 403) - continuing without unfulfilled orders check")
            return {}
        elif r.status_code != 200:
            log(f"⚠️  Failed to get unfulfilled orders: HTTP {r.status_code} - continuing without unfulfilled orders check")
            return {}

        orders = r.json().get("orders", [])
        log(f"📋 Retrieved {len(orders)} unfulfilled orders from Shopify")

        # Extract SKUs and quantities from line items, organized by order
        order_data = {}  # {order_name: {sku: qty}}
        shopify_orders = {}  # {sku: total_qty} - final result
        total_line_items = 0

        for order in orders:
            order_name = order.get("name", "Unknown")
            line_items = order.get("line_items", [])
            log(f"   Order {order_name}: {len(line_items)} line items")

            order_data[order_name] = {}

            for line_item in line_items:
                total_line_items += 1
                sku = line_item.get("sku", "")
                qty = line_item.get("quantity", 0)
                product_title = line_item.get("title", "Unknown Product")

                if sku:
                    order_data[order_name][sku] = qty
                    log(f"     - SKU: {sku}, Qty: {qty}, Product: {product_title}")
                else:
                    log(f"     - ⚠️  Missing SKU for product: {product_title}")

        log(f"📊 Total line items processed: {total_line_items}")

        # Small delay after API call
        time.sleep(0.1)

        if not order_data:
            log("📊 No orders found")
            return {}

        # Check which orders are already processed (in orderstatus table)
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        order_names = list(order_data.keys())
        placeholders = ','.join(['%s'] * len(order_names))

        log(f"🔍 Checking orderstatus table for these orders: {order_names}")

        cur.execute(f"""
            SELECT DISTINCT ordernum
            FROM orderstatus
            WHERE ordernum IN ({placeholders})
        """, order_names)

        processed_orders = {row[0] for row in cur.fetchall()}
        cur.close()
        conn.close()

        if processed_orders:
            log(f"📋 Found {len(processed_orders)} orders already in orderstatus: {list(processed_orders)}")
        else:
            log("📋 No orders found in orderstatus table")

        # Only include SKUs from orders that haven't been processed yet
        for order_name, skus in order_data.items():
            if order_name not in processed_orders:
                log(f"✅ Including order {order_name} (not in orderstatus)")
                for sku, qty in skus.items():
                    shopify_orders[sku] = shopify_orders.get(sku, 0) + qty
            else:
                log(f"⏭️  Skipping order {order_name} (already in orderstatus)")

        log(f"📊 Final unique SKUs: {len(shopify_orders)} with total quantity: {sum(shopify_orders.values())}")

        if shopify_orders:
            log(f"✅ Final result: {len(shopify_orders)} SKUs with unfulfilled orders not in orderstatus")
            for sku, qty in shopify_orders.items():
                log(f"   - {sku}: {qty} items")
            log(f"✅ Total unfulfilled items: {sum(shopify_orders.values())}")
        else:
            log("✅ No unfulfilled orders found that aren't already in orderstatus")

        return shopify_orders

    except Exception as e:
        log(f"⚠️  Error getting unfulfilled orders: {e} - continuing without unfulfilled orders check")
        return {}


def main():
    single_code = sys.argv[1] if len(sys.argv) > 1 else None

    log("=== SHOPIFY INVENTORY SYNC STARTED ===")
    if single_code:
        log(f"Single item mode: {single_code}")
    else:
        log("Full sync mode")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    if single_code:
        cur.execute("SELECT DISTINCT code FROM skumap WHERE code = %s", (single_code,))
    else:
        cur.execute("""
            SELECT DISTINCT sm.code
            FROM skumap sm
            JOIN skusummary ss ON sm.groupid = ss.groupid
            WHERE ss.shopify = 1
        """)

    rows = cur.fetchall()
    codes = [row[0] for row in rows]

    # Get all stock data in one bulk query
    stock_data = calculate_total_stock_bulk(codes, cur)

    # Get all variant data in batches to minimize API calls
    log(f"Fetching variant information for {len(codes)} products...")
    variant_data = batch_search_variants_by_sku(codes)
    log(f"Found variant information for {len(variant_data)} out of {len(codes)} products")

    updated_count = 0
    failed_count = 0
    processed_count = 0
    total_codes = len(codes)
    variant_updates = {}  # Track variant IDs that need database updates
    processed_variants = {}  # Track processed variants for end-of-process correction

    log(f"Starting inventory sync for {total_codes} products (database stock only)...")

    for code in codes:
        processed_count += 1

        # Progress logging every 100 items
        if processed_count % 100 == 0:
            log(f"Progress: {processed_count}/{total_codes} processed, {updated_count} updated, {failed_count} failed")

        # Check if we have variant data from the batch lookup
        if code in variant_data:
            variant_id, inventory_item_id, product_title = variant_data[code]
            # Log the product we found for verification (only for first few to avoid spam)
            if processed_count <= 5:
                log(f"{code}: Found variant {variant_id} in product '{product_title}' (inventory_item_id: {inventory_item_id})")

            # Check if we need to update the stored variant link
            cur.execute("SELECT variantlink FROM skumap WHERE code = %s", (code,))
            row = cur.fetchone()
            stored_variant = row[0].rstrip("V") if row and row[0] else None
            if stored_variant != variant_id:
                variant_updates[code] = variant_id
        else:
            # Try individual lookup if not found in batch - SKU search only, no fallback
            variant_id, inventory_item_id, product_title = get_variant_and_inventory_item(code, cur)
            if not inventory_item_id:
                log(f"{code}: ⚠️  SKU not found in Shopify - skipping inventory update for safety")
                continue

            # Track this variant for database update
            variant_updates[code] = variant_id

        total_qty = stock_data.get(code, 0)

        # Cap stock at 5 for Shopify display (safety measure)
        # Note: Unfulfilled orders will be handled at end of process to minimize timing window
        shopify_qty = min(total_qty, 5)

        # Store variant info for potential end-of-process correction
        processed_variants[code] = {
            'inventory_item_id': inventory_item_id,
            'variant_id': variant_id,
            'product_title': product_title
        }

        current_qty = get_current_shopify_stock(inventory_item_id)
        if current_qty is None:
            log(f"{code}: ⚠️  Could not retrieve current Shopify stock")
            continue

        if current_qty != shopify_qty:
            log(f"{code}: Attempting update from {current_qty} → {shopify_qty} (variant_id: {variant_id}, inventory_item_id: {inventory_item_id})")
            success = set_shopify_inventory(inventory_item_id, shopify_qty)
            if success:
                updated_count += 1
                # Build detailed log message
                log_parts = [f"{code}: ✅ Updated from {current_qty} → {shopify_qty}"]
                if total_qty != shopify_qty:
                    log_parts.append(f"(database stock: {total_qty})")
                if shopify_qty == 5 and total_qty > 5:
                    log_parts.append(f"(capped from {total_qty})")
                log(" ".join(log_parts))
            else:
                failed_count += 1
                log(f"{code}: ❌ Failed to update from {current_qty} → {shopify_qty}")

        # Enhanced rate limiting: pause every 20 API calls (more conservative)
        if processed_count % 20 == 0:
            time.sleep(1.5)  # Longer pause every 20 items

    # Update variant links in database if we found any discrepancies
    update_variant_links_in_database(variant_updates, cur, conn)

    # END-OF-PROCESS: Apply unfulfilled orders correction to minimize timing window
    log("🔄 Starting end-of-process unfulfilled orders correction...")
    unfulfilled_orders = get_unfulfilled_shopify_orders()

    unfulfilled_corrections = 0
    unfulfilled_failed = 0

    if unfulfilled_orders:
        log(f"📋 Processing unfulfilled orders correction for {len(unfulfilled_orders)} SKUs...")

        for sku, pending_qty in unfulfilled_orders.items():
            if sku in processed_variants:
                variant_info = processed_variants[sku]
                inventory_item_id = variant_info['inventory_item_id']
                variant_id = variant_info['variant_id']

                # Get current Shopify stock
                current_qty = get_current_shopify_stock(inventory_item_id)
                if current_qty is None:
                    log(f"{sku}: ⚠️  Could not retrieve current stock for unfulfilled orders correction")
                    continue

                # Calculate corrected quantity (subtract pending orders)
                corrected_qty = max(current_qty - pending_qty, 0)

                if current_qty != corrected_qty:
                    log(f"{sku}: Unfulfilled orders correction: {current_qty} → {corrected_qty} (pending orders: {pending_qty})")
                    success = set_shopify_inventory(inventory_item_id, corrected_qty)
                    if success:
                        unfulfilled_corrections += 1
                        log(f"{sku}: ✅ Corrected for unfulfilled orders: {current_qty} → {corrected_qty}")
                    else:
                        unfulfilled_failed += 1
                        log(f"{sku}: ❌ Failed unfulfilled orders correction: {current_qty} → {corrected_qty}")
            else:
                log(f"{sku}: ⚠️  SKU has unfulfilled orders but wasn't processed in main sync")
    else:
        log("✅ No unfulfilled orders requiring correction")

    cur.close()
    conn.close()

    # Final summary
    total_updates = updated_count + unfulfilled_corrections
    total_failures = failed_count + unfulfilled_failed

    log(f"Main updates: {updated_count}, unfulfilled corrections: {unfulfilled_corrections}")
    log(f"Total updates: {total_updates}, failed: {total_failures}")
    log(f"Mode: {'single' if single_code else 'full'}")
    log("=== SHOPIFY INVENTORY SYNC COMPLETED ===")


if __name__ == "__main__":
    main()



