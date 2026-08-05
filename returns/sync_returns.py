"""
Shopify return sync — books refunded units back out of `sales` as negative rows.

Replaces the monthly PowerBuilder routine `of_shopifyitemreturn`, which read a
hand-exported "shopify item return.csv" out of the Downloads folder. This talks
to the Shopify Refunds API directly, so there is no manual export step and no
month-shaped gap when someone forgets.

WHY THIS IS A SEPARATE SCRIPT (asked and answered, Aug 2026)

  * `orders/update_orders.py` books the sale rows, but it sits under the
    "this logic exists in two places, change both or neither" banner — its live
    twin is bcweb-server/utils/orderSync.js. Putting returns in there would
    create exactly the divergence that banner exists to prevent. It also has
    known whole-run crash modes (`batch::int`) that returns should not share.
  * `db-maint/clean_sales.py` already handles returns, but only *repairs* them,
    on the weekly purge cadence. Ingestion needs to be daily.

  Neither owns sales-and-returns end to end, so this is its own capability.

HOW IT INTERACTS WITH clean_sales.sql

  `db-maint/clean_sales.sql` steps 2-5 repair return rows that arrived with
  soldprice = 0 and then recompute return profit from the current cost. This
  script writes a real soldprice and a real profit up front, so steps 2-4 are
  no-ops for its rows and step 5 is a self-healing backstop that normalises
  them to the same formula. That is deliberate — do not "fix" the overlap.

  The /1.2 refund haircut in the profit model is left intact on purpose: it is
  the margin cushion that keeps pricing viable in a bad month. Return rows
  reverse the original row's profit, so the haircut carries through unchanged.

WHAT IT WILL NOT DO

  A reversal is only written when a matching positive sale row exists and still
  has unreversed units. Shopify refunds also cover cancellations, and
  `update_orders.py` skips cancelled orders at insert time — so without that
  guard a cancelled-before-shipping order would book a negative row against a
  sale that was never recorded, inventing a loss. See `reversible_units()`.

  It does not touch stock. The PowerBuilder routine never restocked either, and
  a returned pair reaching the shelf is a physical goods-in decision.

Run:
    python returns/sync_returns.py                    # rolling 30-day window
    python returns/sync_returns.py --since 2026-06-03 # backfill from a date
    python returns/sync_returns.py --dry-run          # report, write nothing
"""

import argparse
import os
import sys
import time
from datetime import date, datetime, timedelta

import psycopg2
import requests
from dotenv import load_dotenv

# Everything shared lives at the repo root, one level up from this folder.
# Anchored on this file, never the working directory: cron runs with no `cd`,
# so anything relative would land in the invoking user's home instead.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from logging_utils import get_db_config, manage_log_files, create_logger

load_dotenv(dotenv_path=os.path.join(REPO_ROOT, '.env'))
SHOP_DOMAIN = "brookfieldcomfort2.myshopify.com"
ACCESS_TOKEN = os.getenv('SHOPIFY_ORDERS_ACCESS_TOKEN')
API_VERSION = "2024-01"

if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ORDERS_ACCESS_TOKEN not found in .env file")

# Default window. Generous relative to the daily cadence — re-seeing a refund
# costs nothing (the source_key unique index absorbs it) but missing one is
# silent and permanent.
DEFAULT_LOOKBACK_DAYS = 30

SCRIPT_NAME = "sync_returns"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


def safe(value, max_length=None):
    """Convert to string, strip, and truncate for database insertion."""
    result = value.strip() if value and isinstance(value, str) else ""
    if max_length and len(result) > max_length:
        result = result[:max_length]
    return result


# --------------------------------------------------------------------------
# Shopify
# --------------------------------------------------------------------------

def fetch_orders_with_refunds(since):
    """Every order touched since `since`, with its refunds attached.

    Keyed on updated_at, not created_at: issuing a refund updates the order, so
    this catches a July refund against a March order without needing the 90-day
    created_at lookback that month-end/month-export.py uses.
    """
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    params = {
        "updated_at_min": f"{since}T00:00:00+00:00",
        "status": "any",
        "limit": 250,
        "fields": "id,name,created_at,refunds",
    }
    url = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/orders.json"

    orders = []
    page = 1
    while url:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", 2))
            log(f"Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            continue

        if response.status_code != 200:
            raise RuntimeError(
                f"Shopify API {response.status_code}: {response.text}"
            )

        batch = response.json().get("orders", [])
        orders.extend(batch)
        log(f"  page {page}: {len(batch)} orders (total {len(orders)})")

        # Paginate via the Link header. Absent this the fetch silently truncates
        # at 250 — the bug update_orders.py still carries. Don't drop it.
        url = None
        params = None  # cursor URLs already carry the query
        for part in response.headers.get("Link", "").split(","):
            if 'rel="next"' in part:
                url = part.split("<")[1].split(">")[0]
                break

        page += 1
        time.sleep(0.25)

    return orders


def refund_lines(orders, since):
    """Flatten orders into one record per refunded unit-line.

    Shipping-only refunds carry an empty refund_line_items and drop out here,
    which is correct: no goods came back, so no units to reverse.
    """
    out = []
    since_str = str(since)

    for order in orders:
        order_name = safe(order.get("name"), 50)
        for refund in order.get("refunds", []):
            # created_at comes back in shop-local time (+01:00 in BST), so the
            # date prefix is already the UK date the old CSV's "Day" carried.
            refund_date = safe(refund.get("created_at"))[:10]
            if not refund_date or refund_date < since_str:
                continue

            for rli in refund.get("refund_line_items", []):
                quantity = int(rli.get("quantity") or 0)
                if quantity <= 0:
                    continue

                line_item = rli.get("line_item") or {}
                code = safe(line_item.get("sku"), 50)
                if not code:
                    log(f"WARNING: {order_name} refund line {rli.get('id')} has no SKU - skipped")
                    continue

                # Unit price from what was actually refunded, falling back to
                # the original line price when the subtotal is zero (a fully
                # discounted line, or goodwill handled as an adjustment).
                subtotal = float(rli.get("subtotal") or 0)
                unit_price = round(subtotal / quantity, 2) if subtotal else None
                if not unit_price:
                    unit_price = round(float(line_item.get("price") or 0), 2)

                out.append({
                    "source_key": f"SHP:R:{order_name}:{rli.get('id')}",
                    "returnsaleid": str(rli.get("id") or ""),
                    "ordernum": order_name,
                    "code": code,
                    "solddate": refund_date,
                    "qty": quantity,
                    "unit_price": unit_price,
                })

    return out


# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------

def lookup_product(cursor, code):
    """groupid / title / brand for a SKU, or None when it can't be resolved.

    Mirrors the PowerBuilder routine, which skipped a line outright when either
    skumap or skusummary came up empty rather than writing a half-formed row.
    """
    cursor.execute(
        "SELECT groupid FROM skumap WHERE code = %s AND deleted = 0 LIMIT 1",
        (code,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    groupid = row[0]

    cursor.execute("SELECT brand FROM skusummary WHERE groupid = %s LIMIT 1", (groupid,))
    row = cursor.fetchone()
    if not row:
        return None
    brand = row[0]

    cursor.execute("SELECT shopifytitle FROM title WHERE groupid = %s LIMIT 1", (groupid,))
    row = cursor.fetchone()
    productname = row[0] if row else ""

    return {"groupid": groupid, "brand": brand, "productname": productname}


def already_booked(cursor, source_key):
    """True if this exact refund line has already been written.

    Checked before reversible_units() rather than relying on the ON CONFLICT
    alone. Without it a re-run reports its own previous work as "no sale to
    reverse" — because the reversal it already made is what consumed the units.
    On a daily cadence that is ~140 misleading lines a night. The ON CONFLICT
    stays as the real guarantee; this is for a log a human can trust.
    """
    cursor.execute("SELECT 1 FROM sales WHERE source_key = %s LIMIT 1", (source_key,))
    return cursor.fetchone() is not None


def reversible_units(cursor, ordernum, code):
    """Units of this SKU on this order that were sold and not yet reversed.

    Returns (available, unit_profit). `unit_profit` is the per-unit profit of
    the original sale, positive; the caller negates it.

    Nets the positive and negative rows rather than looking only at the sale, so
    a second refund against an already-fully-returned line cannot double-reverse
    it. Guards against a phantom negative when the sale was never booked at all
    — which is the normal case for an order cancelled before fulfilment, since
    update_orders.py skips those.
    """
    cursor.execute(
        """
        SELECT COALESCE(SUM(qty), 0)
        FROM sales
        WHERE channel = 'SHP' AND ordernum = %s AND code = %s
        """,
        (ordernum, code),
    )
    available = int(cursor.fetchone()[0] or 0)

    cursor.execute(
        """
        SELECT profit, qty
        FROM sales
        WHERE channel = 'SHP' AND ordernum = %s AND code = %s AND qty > 0
        ORDER BY id
        LIMIT 1
        """,
        (ordernum, code),
    )
    row = cursor.fetchone()
    unit_profit = None
    if row and row[0] is not None and row[1]:
        unit_profit = round(float(row[0]) / int(row[1]), 2)

    return available, unit_profit


def insert_return(cursor, line, product, unit_profit):
    """Write the negative sale row. Idempotent on source_key.

    profit is the original row's per-unit figure negated, so a sale and its
    return net to ~zero. When the original carried NULL profit (unknown cost)
    this stores NULL rather than a wrong number — clean_sales.sql step 5 fills
    it in on the weekly pass once the inputs exist.

    ordertime and paytype are written as '' to match the shape of the rows the
    PowerBuilder routine left behind.
    """
    cursor.execute(
        """
        INSERT INTO sales (
            channel, code, solddate, groupid, ordernum, ordertime,
            qty, soldprice, productname, brand, profit,
            returnsaleid, source_key
        )
        VALUES ('SHP', %s, %s::date, %s, %s, '', %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_key) WHERE source_key IS NOT NULL DO NOTHING
        """,
        (
            line["code"],
            line["solddate"],
            safe(product["groupid"], 50),
            line["ordernum"],
            -line["qty"],
            line["unit_price"],
            safe(product["productname"], 200),
            safe(product["brand"], 50),
            -unit_profit if unit_profit is not None else None,
            safe(line["returnsaleid"], 50),
            line["source_key"],
        ),
    )
    return cursor.rowcount


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Sync Shopify refunds into sales as return rows")
    parser.add_argument(
        "--since",
        help=f"Earliest refund date, YYYY-MM-DD (default: {DEFAULT_LOOKBACK_DAYS} days ago)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report only, write nothing")
    args = parser.parse_args()

    if args.since:
        try:
            since = datetime.strptime(args.since, "%Y-%m-%d").date()
        except ValueError:
            parser.error("--since must be YYYY-MM-DD")
    else:
        since = date.today() - timedelta(days=DEFAULT_LOOKBACK_DAYS)

    log("=== Return Sync Started ===")
    log(f"Refunds since {since}" + (" (DRY RUN)" if args.dry_run else ""))

    conn = None
    cursor = None
    try:
        orders = fetch_orders_with_refunds(since)
        lines = refund_lines(orders, since)
        log(f"{len(lines)} refunded unit-lines in window")

        conn = psycopg2.connect(**get_db_config())
        cursor = conn.cursor()

        inserted = skipped_existing = skipped_unmatched = skipped_product = 0
        units = 0

        for line in lines:
            if already_booked(cursor, line["source_key"]):
                skipped_existing += 1
                continue

            product = lookup_product(cursor, line["code"])
            if not product:
                log(f"WARNING: {line['ordernum']} {line['code']} - no skumap/skusummary row, skipped")
                skipped_product += 1
                continue

            available, unit_profit = reversible_units(cursor, line["ordernum"], line["code"])
            if available <= 0:
                # Cancelled before the sale was ever booked, or already fully
                # reversed. Either way there is nothing to take back out.
                log(f"INFO: {line['ordernum']} {line['code']} - no unreversed sale to reverse, skipped")
                skipped_unmatched += 1
                continue

            qty = min(line["qty"], available)
            if qty < line["qty"]:
                log(f"WARNING: {line['ordernum']} {line['code']} - refund of {line['qty']} "
                    f"capped at {qty} unreversed unit(s)")
            line = dict(line, qty=qty)

            if unit_profit is None:
                log(f"WARNING: {line['ordernum']} {line['code']} - original profit unknown, "
                    f"storing NULL (clean_sales.sql will fill it)")

            if args.dry_run:
                log(f"DRY RUN would insert: {line['solddate']} {line['ordernum']} {line['code']} "
                    f"qty=-{qty} price={line['unit_price']} profit="
                    f"{-unit_profit if unit_profit is not None else None}")
                inserted += 1
                units += qty
                continue

            if insert_return(cursor, line, product, unit_profit):
                log(f"Return booked: {line['solddate']} {line['ordernum']} {line['code']} "
                    f"qty=-{qty} price={line['unit_price']}")
                inserted += 1
                units += qty
            else:
                skipped_existing += 1

        if args.dry_run:
            conn.rollback()
        else:
            conn.commit()

        log(f"Done: {inserted} returns booked ({units} units), "
            f"{skipped_existing} already present, "
            f"{skipped_unmatched} with no sale to reverse, "
            f"{skipped_product} unresolvable SKUs")

    except Exception as e:
        log(f"ERROR: {e}")
        if conn:
            conn.rollback()
        # Fail loudly. This runs unattended; a silent non-zero-work run is how
        # the old monthly routine lost April 2026.
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        log("=== Script Finished ===")


if __name__ == "__main__":
    main()
