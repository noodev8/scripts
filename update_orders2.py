
import psycopg2
import requests
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
import random
from dotenv import load_dotenv
from logging_utils import get_db_config
import sys

# === CONFIGURATION ===
load_dotenv('.env')
SHOP_DOMAIN = "brookfieldcomfort2.myshopify.com"
ACCESS_TOKEN = os.getenv('SHOPIFY_ORDERS_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ORDERS_ACCESS_TOKEN not found in .env file")

ENABLE_DELETION = False
DELETION_DAYS_THRESHOLD = 5
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "order_sync.log")
LOG_MAX_SIZE = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 3

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logging()
logger.info("=== Order Sync Script Started ===")

def safe(value):
    return value.strip() if value and isinstance(value, str) else ""

def format_datetime(dt_str):
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).strftime("%Y%m%d %H:%M:%S")
    except (ValueError, TypeError):
        return ""

def run_pick_allocation(cursor):
    logger.info("Running pick allocation...")
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
            logger.warning(f"Skipping {order_name}, SKU {shopifysku} - invalid quantity: {order_qty}")
            continue

        logger.info(f"Processing {order_name}, SKU {shopifysku} - need {order_qty} picks")

        # First check how many picks are already allocated to this order
        cursor.execute("""
            SELECT COUNT(*) FROM localstock
            WHERE code = %s AND ordernum = %s AND deleted = 0
        """, (shopifysku, order_name))
        already_allocated = cursor.fetchone()[0]

        if already_allocated >= order_qty:
            logger.info(f"Order {order_name}, SKU {shopifysku} already fully allocated: {already_allocated}/{order_qty} picks")
            # Set orderdate to mark as picked and localstock to the number of picks allocated
            cursor.execute("""
                UPDATE orderstatus SET orderdate = CURRENT_DATE, localstock = %s
                WHERE ordernum = %s AND shopifysku = %s
            """, (already_allocated, order_name, shopifysku))
            continue

        picks_needed = order_qty - already_allocated
        logger.info(f"Order {order_name}, SKU {shopifysku} needs {picks_needed} more picks (already have {already_allocated}/{order_qty})")

        # Get all available stock for this SKU
        query = """
            SELECT id, qty, location, groupid, supplier, brand FROM localstock
            WHERE code = %s AND ordernum = '#FREE' AND (deleted = 0 OR deleted IS NULL) AND allocated = 'unallocated'
            ORDER BY location, id
        """
        logger.info(f"Executing query: {query} with SKU: {shopifysku}")
        cursor.execute(query, (shopifysku,))
        available_picks = cursor.fetchall()
        logger.info(f"Raw query result: {available_picks}")

        logger.info(f"Found {len(available_picks)} available #FREE stock rows for {shopifysku}")
        for i, pick in enumerate(available_picks):
            logger.info(f"  Stock {i+1}: id={pick[0]}, qty={pick[1]}, location={pick[2]}")

        if not available_picks:
            logger.warning(f"No available localstock for {order_name}, SKU {shopifysku}")

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
                logger.info(f"Found {amz_available} AMZ stock for {order_name}, SKU {shopifysku} - allocating {amz_to_allocate}")

                # Set amz column with the amount allocated (no orderdate for AMZ)
                cursor.execute("""
                    UPDATE orderstatus SET amz = %s
                    WHERE ordernum = %s AND shopifysku = %s
                """, (amz_to_allocate, order_name, shopifysku))

                logger.info(f"Order {order_name}, SKU {shopifysku} allocated from AMZ: {amz_to_allocate}/{picks_needed}")
                continue

            # Check supplier using skumap table (shopifysku in orderstatus = code in skumap)
            cursor.execute("""
                SELECT supplier FROM skumap
                WHERE code = %s AND supplier IS NOT NULL AND TRIM(supplier) != ''
                LIMIT 1
            """, (shopifysku,))
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
                        logger.info(f"Found {ukd_available} UKD stock for {order_name}, SKU {shopifysku} - marking UKD with {ukd_to_allocate}")
                        cursor.execute("""
                            UPDATE orderstatus SET ukd = %s 
                            WHERE ordernum = %s AND shopifysku = %s
                        """, (ukd_to_allocate, order_name, shopifysku))
                    else:
                        # No UKD stock available, mark the amount needed for ordering
                        logger.info(f"No UKD stock available for {order_name}, SKU {shopifysku} - marking UKD with {picks_needed} for ordering")
                        cursor.execute("""
                            UPDATE orderstatus SET ukd = %s
                            WHERE ordernum = %s AND shopifysku = %s
                        """, (picks_needed, order_name, shopifysku))
                else:
                    logger.info(f"No stock found anywhere for {order_name}, SKU {shopifysku} - marking othersupplier with {picks_needed} (supplier: {supplier})")
                    cursor.execute("""
                        UPDATE orderstatus SET othersupplier = %s
                        WHERE ordernum = %s AND shopifysku = %s
                    """, (picks_needed, order_name, shopifysku))
            else:
                logger.info(f"No stock found anywhere for {order_name}, SKU {shopifysku} - marking othersupplier with {picks_needed} (no supplier info)")
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
                logger.warning(f"No more available stock for {order_name}, SKU {shopifysku} - allocated {picks_allocated}/{picks_needed}")
                break

            # Take the first available pick
            pick_id, pick_qty, location, groupid, supplier, brand = available_picks[0]
            logger.info(f"Allocating pick {picks_allocated + 1}/{picks_needed}: row {pick_id}, qty={pick_qty}, location={location}")

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
                logger.info(f"Pick split for {order_name}, SKU {shopifysku}, row {pick_id} (location: {location}) -> 1 pick + new row {fallback_id} with {remaining_qty}")
            else:
                # Use the entire pick (qty = 1)
                cursor.execute("UPDATE localstock SET ordernum = %s WHERE id = %s", (order_name, pick_id))
                logger.info(f"Pick assigned for {order_name}, SKU {shopifysku} -> row {pick_id} (location: {location})")

            picks_allocated += 1

            # Note: We'll commit all changes at the end of the function

        total_allocated = already_allocated + picks_allocated

        # Set orderdate and localstock for ANY picks found to prevent double picking
        if picks_allocated > 0:
            cursor.execute("""
                UPDATE orderstatus SET orderdate = CURRENT_DATE, localstock = %s
                WHERE ordernum = %s AND shopifysku = %s
            """, (total_allocated, order_name, shopifysku))

            if total_allocated == order_qty:
                logger.info(f"Order {order_name}, SKU {shopifysku} fully allocated: {total_allocated}/{order_qty} picks")
            else:
                logger.warning(f"Order {order_name}, SKU {shopifysku} partially allocated: {total_allocated}/{order_qty} picks")
        else:
            logger.warning(f"Order {order_name}, SKU {shopifysku} - no new picks allocated")

def run_order_sync(cursor):
    url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/orders.json"
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    params = {
        "financial_status": "paid",
        "fulfillment_status": "unfulfilled",
        "limit": 250,
        "status": "open"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        logger.error(f"Shopify API Error: {response.status_code} - {response.text}")
        return

    orders = response.json().get("orders", [])
    logger.info(f"Retrieved {len(orders)} unfulfilled orders from Shopify")

    # Track current orders from Shopify to identify orders to archive
    current_shopify_orders = set()
    for order in orders:
        if order.get("financial_status") != "paid" or \
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
                logger.warning(f"WARNING: Skipping item with missing SKU in order {order_name}")
                continue

            # Track this order+SKU combination as current
            current_shopify_orders.add((order_name, shopifysku))

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
                logger.info(f"Updated existing order {order_name}, SKU {shopifysku}")
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
                    "0", "", safe(item.get("title")), "Summer",
                    safe(shipping.get("zip")), safe(shipping.get("address1")),
                    safe(shipping.get("address2")), safe(shipping.get("company")),
                    safe(shipping.get("city")), safe(shipping.get("province_code")),
                    safe(shipping.get("country_code")), safe(shipping.get("phone")),
                    shipping_notes, "", 0, 0, 0, 0,
                    "", None, 0, safe(order.get("email")), courier, 0, 0, None, None,
                    "", "SHOPIFY", None, None, None, 0, shipping_cost, 1, None,
                    datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).date(), 0, None
                ))
                logger.info(f"Inserted new order {order_name}, SKU {shopifysku}")

    # Archive orders that are no longer in Shopify
    archive_old_orders(cursor, current_shopify_orders)

def archive_old_orders(cursor, current_shopify_orders):
    """
    Archive orders from orderstatus that are no longer in the current Shopify data.
    This helps keep the UI clean by removing old and fulfilled orders.
    """
    logger.info("Checking for orders to archive...")

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
        logger.info(f"Found {len(orders_to_archive)} orders to archive")

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

            logger.info(f"Archived order {order_name}, SKU {shopifysku}")
    else:
        logger.info("No orders need to be archived")

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
            logger.info("Running full order sync and pick allocation...")
            run_order_sync(cursor)
            logger.info("Order sync completed, now running pick allocation...")
            run_pick_allocation(cursor)

        conn.commit()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("=== Script Finished ===")

if __name__ == '__main__':
    main()

#timestamp with timezone 
