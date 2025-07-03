
import psycopg2
import requests
from datetime import datetime
import os
import random
from dotenv import load_dotenv
from logging_utils import get_db_config, manage_log_files, create_logger
import sys

# === CONFIGURATION ===
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
SHOP_DOMAIN = "brookfieldcomfort2.myshopify.com"
ACCESS_TOKEN = os.getenv('SHOPIFY_ORDERS_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ORDERS_ACCESS_TOKEN not found in .env file")

ENABLE_DELETION = False
DELETION_DAYS_THRESHOLD = 5

# Setup logging using the standardized logging_utils
SCRIPT_NAME = "update_orders2"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)
log("=== Order Sync Script Started ===")

def safe(value):
    return value.strip() if value and isinstance(value, str) else ""

def format_datetime(dt_str):
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).strftime("%Y%m%d %H:%M:%S")
    except (ValueError, TypeError):
        return ""

def get_current_datetime():
    """Get current datetime in YYYYMMDD HH:MM:SS format"""
    return datetime.now().strftime("%Y%m%d %H:%M:%S")

def get_supplier_for_sku(cursor, shopifysku):
    """Get supplier from skusummary table for a given SKU"""
    try:
        # First get groupid from skumap using the code (SKU)
        cursor.execute("SELECT groupid FROM skumap WHERE code = %s LIMIT 1", (shopifysku,))
        result = cursor.fetchone()

        if not result:
            log(f"WARNING: No groupid found in skumap for SKU {shopifysku}")
            return ""

        groupid = result[0]

        # Then get supplier from skusummary using the groupid
        cursor.execute("""
            SELECT supplier FROM skusummary
            WHERE groupid = %s AND supplier IS NOT NULL AND TRIM(supplier) != ''
            LIMIT 1
        """, (groupid,))
        result = cursor.fetchone()
        return result[0] if result else ""

    except Exception as e:
        log(f"WARNING: Could not get supplier for SKU {shopifysku}: {e}")
        return ""

def insert_into_sales(cursor, order, item, shopifysku, order_name):
    """Insert order into sales table"""
    try:
        # Get groupid from skumap
        cursor.execute("SELECT groupid FROM skumap WHERE code = %s LIMIT 1", (shopifysku,))
        result = cursor.fetchone()
        groupid = result[0] if result else None

        if not groupid:
            log(f"WARNING: No groupid found for SKU {shopifysku} (Order {order_name}) - skipping sales insert")
            return

        # Get brand from skusummary
        cursor.execute("SELECT brand FROM skusummary WHERE groupid = %s LIMIT 1", (groupid,))
        result = cursor.fetchone()
        brand = result[0] if result else None

        # Extract sales data
        soldprice = float(item.get("price", 0))
        solddate = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).date()
        ordertime = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).strftime("%H:%M")
        paytype = ",".join(order.get("payment_gateway_names", [])) or "UNKNOWN"
        title = safe(item.get("title"))

        log(f"Inserting into sales: SKU={shopifysku}, Order={order_name}, Qty={item.get('quantity')}, Price={soldprice}, PayType={paytype}")

        # Insert into sales table
        cursor.execute("""
            INSERT INTO sales (
                code, solddate, groupid, ordernum, ordertime, qty,
                soldprice, channel, paytype, collectedvat,
                productname, brand, profit, discount
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, (
            shopifysku, solddate, groupid, order_name, ordertime,
            item.get("quantity"), soldprice, "SHP",
            paytype, None, title, brand, 0, 0
        ))

        log("Sale inserted successfully")

    except Exception as e:
        log(f"ERROR: Failed to insert sale for {order_name}, SKU {shopifysku}: {e}")

def run_pick_allocation(cursor):
    log("Running pick allocation...")
    cursor.execute("""
        SELECT ordernum, shopifysku, qty FROM orderstatus
        WHERE ordertype NOT IN (3, 5)
          AND batch::int != -1
          AND COALESCE(amz, 0) = 0
          AND COALESCE(localstock, 0) = 0
          AND COALESCE(ukd, 0) = 0
          AND COALESCE(othersupplier, 0) = 0
    """)
    orders = cursor.fetchall()
    for order_name, shopifysku, order_qty in orders:
        # Skip if order_qty is None or invalid
        if not order_qty or order_qty <= 0:
            log(f"WARNING: Skipping {order_name}, SKU {shopifysku} - invalid quantity: {order_qty}")
            continue

        log(f"Processing {order_name}, SKU {shopifysku} - need {order_qty} picks")

        # First check how many picks are already allocated to this order
        cursor.execute("""
            SELECT COUNT(*) FROM localstock
            WHERE code = %s AND ordernum = %s AND deleted = 0
        """, (shopifysku, order_name))
        already_allocated = cursor.fetchone()[0]

        if already_allocated >= order_qty:
            log(f"Order {order_name}, SKU {shopifysku} already fully allocated: {already_allocated}/{order_qty} picks")
            # Set orderdate to mark as picked and localstock to the number of picks allocated
            cursor.execute("""
                UPDATE orderstatus SET orderdate = %s, localstock = %s
                WHERE ordernum = %s AND shopifysku = %s
            """, (get_current_datetime(), already_allocated, order_name, shopifysku))
            continue

        picks_needed = order_qty - already_allocated
        log(f"Order {order_name}, SKU {shopifysku} needs {picks_needed} more picks (already have {already_allocated}/{order_qty})")

        # Get all available stock for this SKU
        query = """
            SELECT id, qty, location, groupid, supplier, brand FROM localstock
            WHERE code = %s AND ordernum = '#FREE' AND (deleted = 0 OR deleted IS NULL) AND allocated = 'unallocated'
            ORDER BY location, id
        """
        log(f"Executing query: {query} with SKU: {shopifysku}")
        cursor.execute(query, (shopifysku,))
        available_picks = cursor.fetchall()
        log(f"Raw query result: {available_picks}")

        log(f"Found {len(available_picks)} available #FREE stock rows for {shopifysku}")
        for i, pick in enumerate(available_picks):
            log(f"  Stock {i+1}: id={pick[0]}, qty={pick[1]}, location={pick[2]}")

        if not available_picks:
            log(f"WARNING: No available localstock for {order_name}, SKU {shopifysku}")

            # Check amzfeed table for amzlive stock
            cursor.execute("""
                SELECT SUM(amzlive) FROM amzfeed
                WHERE code = %s AND amzlive > 0
            """, (shopifysku,))
            amz_result = cursor.fetchone()
            amz_available = amz_result[0] if amz_result and amz_result[0] else 0

            if amz_available > 0:
                # Calculate how much AMZ stock to allocate (min of what's needed vs what's available)
                amz_to_allocate = min(picks_needed, amz_available)
                log(f"Found {amz_available} AMZ stock for {order_name}, SKU {shopifysku} - allocating {amz_to_allocate}")

                # Set amz column with the amount allocated (no orderdate for AMZ)
                cursor.execute("""
                    UPDATE orderstatus SET amz = %s
                    WHERE ordernum = %s AND shopifysku = %s
                """, (amz_to_allocate, order_name, shopifysku))

                log(f"Order {order_name}, SKU {shopifysku} allocated from AMZ: {amz_to_allocate}/{picks_needed}")
                continue

            # Check supplier using skumap -> skusummary lookup
            cursor.execute("SELECT groupid FROM skumap WHERE code = %s LIMIT 1", (shopifysku,))
            groupid_result = cursor.fetchone()
            supplier_result = None

            if groupid_result:
                groupid = groupid_result[0]
                cursor.execute("""
                    SELECT supplier FROM skusummary
                    WHERE groupid = %s AND supplier IS NOT NULL AND TRIM(supplier) != ''
                    LIMIT 1
                """, (groupid,))
                supplier_result = cursor.fetchone()

            if supplier_result:
                supplier = supplier_result[0]
                # Check if supplier is 'ukd' (case insensitive)
                if supplier and supplier.lower() == 'ukd':
                    # Check ukdstock table for available stock
                    cursor.execute("""
                        SELECT SUM(stock) FROM ukdstock
                        WHERE code = %s AND stock > 0
                    """, (shopifysku,))
                    ukd_result = cursor.fetchone()
                    ukd_available = ukd_result[0] if ukd_result and ukd_result[0] else 0

                    if ukd_available > 0:
                        # Calculate how much UKD stock to allocate (min of what's needed vs what's available)
                        ukd_to_allocate = min(picks_needed, ukd_available)
                        log(f"Found {ukd_available} UKD stock for {order_name}, SKU {shopifysku} - marking UKD with {ukd_to_allocate}")
                        cursor.execute("""
                            UPDATE orderstatus SET ukd = %s
                            WHERE ordernum = %s AND shopifysku = %s
                        """, (ukd_to_allocate, order_name, shopifysku))
                    else:
                        # No UKD stock available, mark the amount needed for ordering
                        log(f"No UKD stock available for {order_name}, SKU {shopifysku} - marking UKD with {picks_needed} for ordering")
                        cursor.execute("""
                            UPDATE orderstatus SET ukd = %s
                            WHERE ordernum = %s AND shopifysku = %s
                        """, (picks_needed, order_name, shopifysku))
                else:
                    log(f"No stock found anywhere for {order_name}, SKU {shopifysku} - marking othersupplier with {picks_needed} (supplier: {supplier})")
                    cursor.execute("""
                        UPDATE orderstatus SET othersupplier = %s
                        WHERE ordernum = %s AND shopifysku = %s
                    """, (picks_needed, order_name, shopifysku))
            else:
                log(f"No stock found anywhere for {order_name}, SKU {shopifysku} - marking othersupplier with {picks_needed} (no supplier info)")
                cursor.execute("""
                    UPDATE orderstatus SET othersupplier = %s
                    WHERE ordernum = %s AND shopifysku = %s
                """, (picks_needed, order_name, shopifysku))

            continue

        picks_allocated = 0

        while picks_allocated < picks_needed:
            # Re-query available picks each time to include any newly created #FREE rows
            query = """
                SELECT id, qty, location, groupid, supplier, brand FROM localstock
                WHERE code = %s AND ordernum = '#FREE' AND (deleted = 0 OR deleted IS NULL) AND allocated = 'unallocated'
                ORDER BY location, id
            """
            cursor.execute(query, (shopifysku,))
            available_picks = cursor.fetchall()

            if not available_picks:
                log(f"WARNING: No more available stock for {order_name}, SKU {shopifysku} - allocated {picks_allocated}/{picks_needed}")
                break

            # Take the first available pick
            pick_id, pick_qty, location, groupid, supplier, brand = available_picks[0]
            log(f"Allocating pick {picks_allocated + 1}/{picks_needed}: row {pick_id}, qty={pick_qty}, location={location}")

            if pick_qty > 1:
                # Use 1 from this pick and create a new row with the remainder
                cursor.execute("""
                    UPDATE localstock SET qty = 1, ordernum = %s WHERE id = %s
                """, (order_name, pick_id))

                remaining_qty = pick_qty - 1
                fallback_id = int(''.join(filter(str.isdigit, order_name)) + str(random.randint(100, 999)))
                cursor.execute("""
                    INSERT INTO localstock (id, updated, ordernum, location, groupid, code, supplier, qty, brand, allocated)
                    VALUES (%s, CURRENT_TIMESTAMP, '#FREE', %s, %s, %s, %s, %s, %s, 'unallocated')
                """, (fallback_id, location, groupid, shopifysku, supplier, remaining_qty, brand))
                log(f"Pick split for {order_name}, SKU {shopifysku}, row {pick_id} (location: {location}) -> 1 pick + new row {fallback_id} with {remaining_qty}")
            else:
                # Use the entire pick (qty = 1)
                cursor.execute("UPDATE localstock SET ordernum = %s WHERE id = %s", (order_name, pick_id))
                log(f"Pick assigned for {order_name}, SKU {shopifysku} -> row {pick_id} (location: {location})")

            picks_allocated += 1

            # Note: We'll commit all changes at the end of the function

        total_allocated = already_allocated + picks_allocated

        # Set orderdate and localstock for ANY picks found to prevent double picking
        if picks_allocated > 0:
            cursor.execute("""
                UPDATE orderstatus SET orderdate = %s, localstock = %s
                WHERE ordernum = %s AND shopifysku = %s
            """, (get_current_datetime(), total_allocated, order_name, shopifysku))

            if total_allocated == order_qty:
                log(f"Order {order_name}, SKU {shopifysku} fully allocated: {total_allocated}/{order_qty} picks")
            else:
                log(f"WARNING: Order {order_name}, SKU {shopifysku} partially allocated: {total_allocated}/{order_qty} picks")
        else:
            log(f"WARNING: Order {order_name}, SKU {shopifysku} - no new picks allocated")

def run_order_sync(cursor):
    url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/orders.json"
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    # Note: We'll fetch all open unfulfilled orders and filter by financial_status in code
    # to include both "paid" and "partially_refunded" orders
    params = {
        "fulfillment_status": "unfulfilled",
        "limit": 250,
        "status": "open"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        log(f"ERROR: Shopify API Error: {response.status_code} - {response.text}")
        return

    orders = response.json().get("orders", [])
    log(f"Retrieved {len(orders)} unfulfilled orders from Shopify")

    # Track current orders from Shopify to identify orders to archive
    current_shopify_orders = set()
    for order in orders:
        # Allow both "paid" and "partially_refunded" orders (e.g., when shipping is refunded)
        # but exclude cancelled or fulfilled orders
        financial_status = order.get("financial_status")
        if financial_status not in ["paid", "partially_refunded"] or \
           order.get("fulfillment_status") not in ["unfulfilled", None] or \
           order.get("cancel_reason") is not None:
            continue

        order_name = order["name"]
        shipping = order.get("shipping_address", {}) or {}
        shipping_cost_str = order.get("total_shipping_price_set", {}).get("shop_money", {}).get("amount")
        shipping_cost = float(shipping_cost_str) if shipping_cost_str else None
        shipping_notes = safe(order.get("note"))
        courier = 4 if shipping_cost == 5.95 else 5

        for item in order.get("line_items", []):
            shopifysku = safe(item.get("sku"))
            if not shopifysku:
                log(f"WARNING: Skipping item with missing SKU in order {order_name}")
                continue

            # Track this order+SKU combination as current
            current_shopify_orders.add((order_name, shopifysku))

            # Get supplier for this SKU
            supplier = get_supplier_for_sku(cursor, shopifysku)

            cursor.execute("SELECT 1 FROM orderstatus WHERE ordernum = %s AND shopifysku = %s", (order_name, shopifysku))
            exists = cursor.fetchone() is not None

            if exists:
                cursor.execute("""
                    UPDATE orderstatus SET
                        shippingname = %s,
                        postcode = %s,
                        address1 = %s,
                        address2 = %s,
                        company = %s,
                        city = %s,
                        county = %s,
                        country = %s,
                        phone = %s,
                        shippingnotes = %s,
                        email = %s,
                        last_seen = CURRENT_TIMESTAMP
                    WHERE ordernum = %s AND shopifysku = %s
                """, (
                    safe(shipping.get("name")),
                    safe(shipping.get("zip")),
                    safe(shipping.get("address1")),
                    safe(shipping.get("address2")),
                    safe(shipping.get("company")),
                    safe(shipping.get("city")),
                    safe(shipping.get("province_code")),
                    safe(shipping.get("country_code")),
                    safe(shipping.get("phone")),
                    shipping_notes,
                    safe(order.get("email")),
                    order_name,
                    shopifysku
                ))
                log(f"Updated existing order {order_name}, SKU {shopifysku}")
            else:
                cursor.execute("""
                    INSERT INTO orderstatus (
                        ordernum, shopifysku, qty, updated, created, batch, supplier, title, shippingname,
                        postcode, address1, address2, company, city, county, country, phone, shippingnotes,
                        orderdate, ukd, localstock, amz, othersupplier, fnsku, weight, pickedqty, email,
                        courier, courierfixed, customerwaiting, notorderamz, alloworder, searchalt, channel,
                        picknotfound, fbaordered, notes, shopcustomer, shippingcost, ordertype, ponumber,
                        createddate, arrived, arriveddate
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    order_name, shopifysku, item.get("quantity"),
                    format_datetime(order["updated_at"]),
                    format_datetime(order["created_at"]),
                    "0", supplier, safe(item.get("title")), safe(shipping.get("name")),
                    safe(shipping.get("zip")), safe(shipping.get("address1")),
                    safe(shipping.get("address2")), safe(shipping.get("company")),
                    safe(shipping.get("city")), safe(shipping.get("province_code")),
                    safe(shipping.get("country_code")), safe(shipping.get("phone")),
                    shipping_notes, "", 0, 0, 0, 0,
                    "", None, 0, safe(order.get("email")), courier, 0, 0, None, None,
                    "", "SHOPIFY", None, None, None, 0, shipping_cost, 1, None,
                    datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).date(), 0, None
                ))
                log(f"Inserted new order {order_name}, SKU {shopifysku} (supplier: {supplier})")

                # Insert into sales table
                insert_into_sales(cursor, order, item, shopifysku, order_name)

    # Archive orders that are no longer in Shopify
    archive_old_orders(cursor, current_shopify_orders)

def remove_done_picks_from_localstock(cursor):
    """
    Remove done picks from localstock for orders that have been fulfilled/archived.
    This prevents completed picks from showing up on the picklist.
    """
    log("Removing done picks from localstock...")

    try:
        # Delete picks from localstock where:
        # - ordernum is not null and starts with 'BC%' (Brookfield Comfort orders)
        # - ordernum is not in orderstatus (meaning the order has been fulfilled/archived)
        cursor.execute("""
            DELETE FROM localstock
            WHERE ordernum IS NOT NULL
              AND ordernum LIKE 'BC%'
              AND ordernum NOT IN (
                SELECT DISTINCT ordernum FROM orderstatus
              )
        """)

        deleted_count = cursor.rowcount
        if deleted_count > 0:
            log(f"Removed {deleted_count} completed picks from localstock")
        else:
            log("No done picks found to remove from localstock")

    except Exception as e:
        log(f"ERROR: Failed to remove completed picks from localstock: {e}")

def archive_old_orders(cursor, current_shopify_orders):
    """
    Archive orders from orderstatus that are no longer in the current Shopify data.
    This helps keep the UI clean by removing old and fulfilled orders.
    """
    log("Checking for orders to archive...")

    # Get all orders currently in orderstatus
    cursor.execute("""
        SELECT ordernum, shopifysku FROM orderstatus
        WHERE channel = 'SHOPIFY'
    """)
    existing_orders = cursor.fetchall()

    orders_to_archive = []
    for order_name, shopifysku in existing_orders:
        if (order_name, shopifysku) not in current_shopify_orders:
            orders_to_archive.append((order_name, shopifysku))

    if orders_to_archive:
        log(f"Found {len(orders_to_archive)} orders to archive")

        for order_name, shopifysku in orders_to_archive:
            # Copy the order to archive table
            cursor.execute("""
                INSERT INTO orderstatus_archive
                SELECT * FROM orderstatus
                WHERE ordernum = %s AND shopifysku = %s
            """, (order_name, shopifysku))

            # Remove from orderstatus
            cursor.execute("""
                DELETE FROM orderstatus
                WHERE ordernum = %s AND shopifysku = %s
            """, (order_name, shopifysku))

            log(f"Archived order {order_name}, SKU {shopifysku}")

        # After archiving orders, remove done picks from localstock
        remove_done_picks_from_localstock(cursor)
    else:
        log("No orders need to be archived")

def main():
    pick_only = '--picks' in sys.argv
    conn = None
    cursor = None
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        if pick_only:
            # Only run pick allocation
            run_pick_allocation(cursor)
        else:
            # Run both order sync and pick allocation in sequence
            log("Running full order sync and pick allocation...")
            run_order_sync(cursor)
            log("Order sync completed, now running pick allocation...")
            run_pick_allocation(cursor)

        conn.commit()
    except Exception as e:
        log(f"ERROR: Unexpected error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        log("=== Script Finished ===")

if __name__ == '__main__':
    main()

#timestamp with timezone 
