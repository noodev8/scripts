import psycopg2
import requests
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
from dotenv import load_dotenv
from logging_utils import get_db_config

# === CONFIGURATION ===
# Load environment variables from .env
load_dotenv('.env')

SHOP_DOMAIN = "brookfieldcomfort2.myshopify.com"
ACCESS_TOKEN = os.getenv('SHOPIFY_ORDERS_ACCESS_TOKEN')

# Validate that the access token was loaded
if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ORDERS_ACCESS_TOKEN not found in .env file")

# Safety settings for order deletion
ENABLE_DELETION = False  # Set to True to enable deletion of old orders
DELETION_DAYS_THRESHOLD = 5  # Only delete orders not seen for this many days

# Logging configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "order_sync.log")
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5MB per log file
LOG_BACKUP_COUNT = 3  # Keep 3 backup files (total ~20MB max)



# === SETUP LOGGING ===
def setup_logging():
    """Setup rotating file logger to prevent log files from getting too big"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT
    )

    # Create console handler for immediate feedback
    console_handler = logging.StreamHandler()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize logging
logger = setup_logging()
logger.info("=== Order Sync Script Started ===")

# === HELPER FUNCTIONS ===
def safe(value):
    return value.strip() if value and isinstance(value, str) else ""

def format_datetime(dt_str):
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).strftime("%Y%m%d %H:%M:%S")
    except (ValueError, TypeError):
        return ""

# === CONNECT TO POSTGRES ===
conn = None
cursor = None
try:
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    insert_order_sql = """
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
    """

    insert_sales_sql = """
        INSERT INTO sales (
            code, solddate, groupid, ordernum, ordertime, qty,
            soldprice, channel, paytype, collectedvat,
            productname, brand, profit, discount
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    update_sql = """
        UPDATE orderstatus
        SET
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
    """

    # SQL to update last_seen for orders that still exist in Shopify
    update_last_seen_sql = """
        UPDATE orderstatus
        SET last_seen = CURRENT_TIMESTAMP
        WHERE ordernum = %s AND shopifysku = %s
    """

    url = f"https://{SHOP_DOMAIN}/admin/api/2024-01/orders.json"
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    params = {
        "financial_status": "paid",
        "fulfillment_status": "unfulfilled",
        "limit": 250,
        "status": "open"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        orders = response.json().get("orders", [])
        logger.info(f"Retrieved {len(orders)} unfulfilled orders from Shopify")
        unfulfilled_keys = set()

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

                unfulfilled_keys.add((order_name, shopifysku))

                cursor.execute("""SELECT 1 FROM orderstatus WHERE ordernum = %s AND shopifysku = %s""",
                               (order_name, shopifysku))
                exists = cursor.fetchone() is not None

                if exists:
                    try:
                        cursor.execute(update_sql, (
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
                        logger.info(f"Updated existing order {order_name}, SKU {shopifysku} (last_seen updated)")
                    except psycopg2.Error as e:
                        logger.error(f"ERROR: Error updating order {order_name}, SKU {shopifysku}: {e}")
                    continue
                else:
                    # For new orders, also update last_seen after insertion
                    try:
                        cursor.execute(update_last_seen_sql, (order_name, shopifysku))
                    except psycopg2.Error as e:
                        logger.warning(f"WARNING: Error updating last_seen for new order {order_name}, SKU {shopifysku}: {e}")

                # Fetch supplier, fnsku, weight
                supplier, fnsku, weight = "", "", None

                cursor.execute("""SELECT supplier FROM skusummary WHERE groupid = (
                                    SELECT groupid FROM skumap WHERE code = %s LIMIT 1
                                ) LIMIT 1""", (shopifysku,))
                result = cursor.fetchone()
                if result:
                    supplier = result[0]

                cursor.execute("SELECT fnsku FROM amzfeed WHERE TRIM(LOWER(code)) = TRIM(LOWER(%s)) LIMIT 1", (shopifysku,))
                result = cursor.fetchone()
                if result and result[0]:
                    fnsku = result[0]

                cursor.execute("SELECT weight FROM skumap WHERE code = %s LIMIT 1", (shopifysku,))
                result = cursor.fetchone()
                if result and result[0]:
                    weight = result[0]

                try:
                    # Insert into orderstatus
                    cursor.execute(insert_order_sql, (
                        order_name, shopifysku, item.get("quantity"),
                        format_datetime(order["updated_at"]),
                        format_datetime(order["created_at"]),
                        "0", supplier, safe(item.get("title")), safe(shipping.get("name")),
                        safe(shipping.get("zip")), safe(shipping.get("address1")),
                        safe(shipping.get("address2")), safe(shipping.get("company")),
                        safe(shipping.get("city")), safe(shipping.get("province_code")),
                        safe(shipping.get("country_code")), safe(shipping.get("phone")),
                        shipping_notes, "", 0, 0, 0, 0,
                        fnsku, weight, 0, safe(order.get("email")), courier, 0, 0, None, None,
                        "", "SHOPIFY", None, None, None, 0, shipping_cost, 1, None,
                        datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).date(), 0, None
                    ))

                    # === Insert into sales with debug logging ===
                    groupid = None
                    brand = None
                    cursor.execute("SELECT groupid FROM skumap WHERE code = %s LIMIT 1", (shopifysku,))
                    result = cursor.fetchone()
                    if result:
                        groupid = result[0]
                    else:
                        logger.warning(f"WARNING: No groupid found for SKU {shopifysku} (Order {order_name})")

                    if groupid:
                        cursor.execute("SELECT brand FROM skusummary WHERE groupid = %s LIMIT 1", (groupid,))
                        result = cursor.fetchone()
                        brand = result[0] if result else None

                    soldprice = float(item.get("price", 0))
                    solddate = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).date()
                    ordertime = datetime.fromisoformat(order["created_at"].replace("Z", "+00:00")).strftime("%H:%M:%S")
                    paytype = ",".join(order.get("payment_gateway_names", [])) or "UNKNOWN"
                    title = safe(item.get("title"))

                    logger.info(f"Inserting into sales: SKU={shopifysku}, Order={order_name}, Qty={item.get('quantity')}, Price={soldprice}, PayType={paytype}")

                    cursor.execute(insert_sales_sql, (
                        shopifysku, solddate, groupid, order_name, ordertime,
                        item.get("quantity"), soldprice, "SHP",
                        paytype, None, title, brand, 0, 0
                    ))
                    logger.info("Sale inserted successfully")

                except psycopg2.Error as e:
                    logger.error(f"ERROR: Error inserting order/sale {order_name}, SKU {shopifysku}: {e}")

        # === CLEANUP OLD ORDERS (SAFER APPROACH) ===
        if ENABLE_DELETION:
            # Only delete orders not seen for more than DELETION_DAYS_THRESHOLD days
            cursor.execute("""
                SELECT ordernum, shopifysku, last_seen
                FROM orderstatus
                WHERE last_seen < CURRENT_TIMESTAMP - INTERVAL '%s days'
            """, (DELETION_DAYS_THRESHOLD,))

            old_orders = cursor.fetchall()
            logger.info(f"Found {len(old_orders)} orders older than {DELETION_DAYS_THRESHOLD} days")

            for ordernum, shopifysku, last_seen in old_orders:
                try:
                    cursor.execute("DELETE FROM orderstatus WHERE ordernum = %s AND shopifysku = %s", (ordernum, shopifysku))
                    logger.info(f"Deleted old order {ordernum}, SKU {shopifysku} (last seen: {last_seen})")
                except psycopg2.Error as e:
                    logger.error(f"ERROR: Error deleting old order {ordernum}, SKU {shopifysku}: {e}")
        else:
            # Show what WOULD be deleted if deletion was enabled
            cursor.execute("""
                SELECT ordernum, shopifysku, last_seen
                FROM orderstatus
                WHERE last_seen < CURRENT_TIMESTAMP - INTERVAL '%s days'
            """, (DELETION_DAYS_THRESHOLD,))

            old_orders = cursor.fetchall()
            if old_orders:
                logger.info(f"DELETION DISABLED: Found {len(old_orders)} orders that would be deleted (older than {DELETION_DAYS_THRESHOLD} days):")
                for ordernum, shopifysku, last_seen in old_orders[:5]:  # Show first 5 as examples
                    logger.info(f"   - {ordernum}, SKU {shopifysku} (last seen: {last_seen})")
                if len(old_orders) > 5:
                    logger.info(f"   ... and {len(old_orders) - 5} more")
                logger.info(f"To enable deletion, set ENABLE_DELETION = True in the configuration")
            else:
                logger.info(f"No orders older than {DELETION_DAYS_THRESHOLD} days found")

        conn.commit()
        logger.info("All changes committed to the database")
        logger.info("=== Order Sync Script Completed Successfully ===")

    else:
        logger.error(f"Shopify API Error: {response.status_code} - {response.text}")

except psycopg2.Error as e:
    logger.error(f"Database error: {e}")
    if conn:
        conn.rollback()

except requests.exceptions.RequestException as e:
    logger.error(f"API request error: {e}")

except Exception as e:
    logger.error(f"Unexpected error: {e}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    logger.info("=== Order Sync Script Finished ===")
