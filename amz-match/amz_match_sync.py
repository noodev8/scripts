#!/usr/bin/env python3
r"""
=======================================================================================================================
amz_match_sync.py  —  Shopify "match Amazon price" reconcile (self-contained cron job)
=======================================================================================================================
WHAT / WHY
    For every Shopify style FLAGGED with skusummary.match_amazon_price = TRUE, keep its Shopify price pinned to Amazon's
    cheapest IN-STOCK size:

        target = MIN(amzfeed.amzprice)  over that groupid's rows  WHERE amzlive > 0

    Amazon is the CEILING ("never go higher than Amazon lowest"): Shopify is set exactly to that lowest live Amazon price,
    so Shopify stays competitive and Amazon is never undercut by omission. This zeroes the admin on a chosen few styles.

    Source of truth is amzfeed — Amazon's OWN price, refreshed when the operator loads the Amazon file.
    Because we reconcile off amzfeed (not off "the moment someone edits Amazon"), this ALSO catches price changes made
    outside our tools (Seller Central by hand, or an Amazon repricer). It is READ-ONLY on amzfeed (never written).

WHEN
    Cron (see crontab.txt for timing) — scheduled ahead of the Google Merchant feed generation, so the day's changes
    are carried to Google by that feed. A run where nothing changed (Amazon didn't move, or the feed wasn't reloaded)
    is a near-instant no-op that touches NO external API: the diff-guard below only pushes a style whose Amazon-lowest
    actually differs from its live Shopify price. So it is safe to run daily regardless.

WHAT IT DOES per flagged style (mirrors the bcweb Shopify "Apply" write, W1, but automated):
    - no in-stock Amazon size (target is NULL)        -> SKIP, reported as "no_amazon_stock"
    - target < cost                                    -> SKIP, reported as "below_cost" (never sell Shopify at a loss)
    - round(target) == current shopifyprice            -> SKIP, "unchanged" (no DB write, no API call)
    - otherwise CHANGE:
        UPDATE skusummary SET shopifyprice = '<2dp string>'         (NOT shopifychange — we push directly below)
        INSERT price_change_log (groupid,'SHP', old, new, NULL, note, 'Amazon match (auto)')   [audit stays honest]
        then push the new price to Shopify (per variant), reusing the mechanism proven in ../price_update.py.
      If the DIRECT Shopify push fails, we set skusummary.shopifychange = 1 as a safety net so the nightly
      price_update.py sweep re-pushes it (there is no operator watching an automated run).

    Google Merchant is NOT pushed from here. The merchant_feed.py --upload feed (scheduled after this job) regenerates
    the whole feed from the DB, so today's price changes reach Google via that one daily feed (no Content API).

RETIRES CLEANLY: this folder + its one crontab line are the whole feature on the scripts side. Delete both when the
    legacy PowerBuilder app (and its manual amzfeed refresh) goes.

SHARED DEPS (reused from the parent C:\scripts, NOT duplicated): logging_utils.py and .env (DB_* + SHOPIFY_ACCESS_TOKEN).
    Enabling a style is a one-liner until the bcweb UI toggle lands:
        UPDATE skusummary SET match_amazon_price = true WHERE groupid = 'ABC123';

USAGE
    python amz_match_sync.py                 # live reconcile of every flagged style
    python amz_match_sync.py --dry-run       # compute + log what WOULD change; no DB write, no push (run this first)
    python amz_match_sync.py --groupid ABC   # limit to one style (live unless combined with --dry-run)
=======================================================================================================================
"""

import os
import sys
import time
import argparse

# --- Reuse the shared scripts infrastructure that lives one level up (C:\scripts on Windows, /apps/scripts on the VPS).
#     Python only puts THIS script's dir on sys.path, so add the parent before importing the shared logging_utils.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PARENT_DIR)

import psycopg2
import requests
from dotenv import load_dotenv
from logging_utils import manage_log_files, create_logger, get_db_config

# --- Credentials come from the SHARED parent .env (DB_* + SHOPIFY_ACCESS_TOKEN), same as price_update.py. ------------
load_dotenv(dotenv_path=os.path.join(PARENT_DIR, '.env'))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

# The operator recorded against every auto price change so the audit trail + bcweb "Price Changes" tile stay honest.
CHANGED_BY = 'Amazon match (auto)'

if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in the shared .env (C:\\scripts\\.env)")

SCRIPT_NAME = "amz_match_sync"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)


# ---------------------------------------------------------------------------------------------------------------------
# SQL helper — mirror bcweb-server/utils/sql.js safeNumeric(): the legacy price columns (shopifyprice/cost/rrp/amzprice)
# are VARCHAR and can hold junk (real case: rrp = the literal 'RRP'). A bare ::numeric THROWS on those; this returns
# NULL unless the trimmed value looks like a number. ONLY ever pass a hard-coded column expression here (never input).
# ---------------------------------------------------------------------------------------------------------------------
def safe_numeric(col):
    return (f"CASE WHEN btrim({col}::text) ~ '^-?[0-9]+(\\.[0-9]+)?$' "
            f"THEN btrim({col}::text)::numeric ELSE NULL END")


# ---------------------------------------------------------------------------------------------------------------------
# Shopify Admin API — copied (trimmed) from price_update.py. Look a variant up by SKU (never trust a stale cached id),
# then PUT its price (+ compare_at_price from RRP). Per-variant, exactly like the proven nightly sweep.
# ---------------------------------------------------------------------------------------------------------------------
def search_variant_by_sku(sku):
    """Return (variant_id, current_price) for a SKU, or (None, None) if Shopify has no such variant."""
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"}
    query = """
    query($sku: String!) {
        productVariants(first: 1, query: $sku) {
            edges { node { id sku price } }
        }
    }
    """
    payload = {"query": query, "variables": {"sku": f"sku:{sku}"}}
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 429:
            time.sleep(5)
            r = requests.post(url, json=payload, headers=headers)
        if r.status_code != 200:
            return None, None
        data = r.json()
        if "errors" in data:
            log(f"GraphQL error for SKU {sku}: {data['errors']}")
            return None, None
        edges = data.get("data", {}).get("productVariants", {}).get("edges", [])
        if not edges:
            return None, None
        node = edges[0]["node"]
        time.sleep(0.1)
        return node["id"].split("/")[-1], node["price"]
    except Exception as e:
        log(f"Exception searching SKU {sku}: {e}")
        return None, None


def update_variant_price(variant_id, new_price, rrp=None):
    """PUT a variant's price (+ compare_at_price from rrp when valid). Returns True or an error string."""
    if not variant_id:
        return "No variant id"
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/variants/{variant_id}.json"
    headers = {"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"}
    payload = {"variant": {"id": variant_id, "price": str(new_price)}}
    if rrp:
        try:
            rrp_float = float(rrp)
            if rrp_float > 0:
                payload["variant"]["compare_at_price"] = f"{rrp_float:.2f}"
        except (ValueError, TypeError):
            pass
    retries = 5
    while retries > 0:
        try:
            resp = requests.put(url, json=payload, headers=headers)
            if resp.status_code == 200:
                time.sleep(0.1)
                return True
            if resp.status_code == 429:
                time.sleep(max(int(resp.headers.get("Retry-After", "5")), 5))
                retries -= 1
                continue
            return f"HTTP {resp.status_code}"
        except Exception as e:
            return f"Exception — {e}"
    return "Rate limit exceeded"


# ---------------------------------------------------------------------------------------------------------------------
# Push helpers — one style at a time. Volume is tiny (only the flagged styles that actually changed today).
# ---------------------------------------------------------------------------------------------------------------------
def push_shopify_style(cur, groupid, new_price_str, rrp):
    """Set every live variant of this style to new_price_str on Shopify. Returns (ok, pushed, failed)."""
    cur.execute(
        "SELECT code FROM skumap WHERE groupid = %s AND COALESCE(deleted, 0) = 0",
        (groupid,)
    )
    codes = [row[0] for row in cur.fetchall()]
    pushed, failed = 0, 0
    for code in codes:
        variant_id, _current = search_variant_by_sku(code)
        if not variant_id:
            log(f"  {code}: SKU not found in Shopify — skipped (safety)")
            failed += 1
            continue
        result = update_variant_price(variant_id, new_price_str, rrp)
        if result is True:
            pushed += 1
        else:
            failed += 1
            log(f"  {code}: Shopify update failed — {result}")
    return (failed == 0 and pushed > 0), pushed, failed


# ---------------------------------------------------------------------------------------------------------------------
# Main reconcile
# ---------------------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Shopify match-Amazon-price reconcile")
    ap.add_argument("--dry-run", action="store_true", help="compute + log what would change; no DB write, no push")
    ap.add_argument("--groupid", help="limit to a single style")
    args = ap.parse_args()

    started = time.time()
    mode = "DRY-RUN" if args.dry_run else "LIVE"
    scope = f", groupid={args.groupid}" if args.groupid else ""
    log(f"=== amz_match_sync start ({mode}{scope}) ===")

    db = get_db_config()
    conn = psycopg2.connect(**db)
    cur = conn.cursor()

    # One set-based read: every flagged style with its Amazon-lowest-in-stock alongside its current price/cost/rrp/flags.
    # No N+1 — the per-style skumap reads happen only for the handful that actually change.
    sn_price = safe_numeric('ss.shopifyprice')
    sn_cost = safe_numeric('ss.cost')
    sn_rrp = safe_numeric('ss.rrp')
    sn_amz = safe_numeric('amzprice')
    sql = f"""
        SELECT ss.groupid,
               {sn_price}                 AS cur_price,
               {sn_cost}                  AS cost,
               {sn_rrp}                   AS rrp,
               COALESCE(ss.shopify, 0)    AS live,
               amz.lowest                 AS amz_lowest
        FROM skusummary ss
        LEFT JOIN (
            SELECT groupid, MIN({sn_amz}) AS lowest
            FROM amzfeed
            WHERE COALESCE(amzlive, 0) > 0
            GROUP BY groupid
        ) amz ON amz.groupid = ss.groupid
        WHERE ss.match_amazon_price = true
    """
    params = []
    if args.groupid:
        sql += " AND ss.groupid = %s"
        params.append(args.groupid)
    sql += " ORDER BY ss.groupid"
    cur.execute(sql, params)
    rows = cur.fetchall()

    changed = 0
    skip_no_stock = 0
    skip_below_cost = 0
    unchanged = 0
    push_shopify_fail = 0
    report_lines = []

    for groupid, cur_price, cost, rrp, live, amz_lowest in rows:
        # 1) No sellable Amazon size to match to.
        if amz_lowest is None:
            skip_no_stock += 1
            report_lines.append(f"{groupid}: SKIP no_amazon_stock (no in-stock Amazon size)")
            continue

        target = round(float(amz_lowest), 2)
        target_str = f"{target:.2f}"

        # 2) Never set Shopify below cost (the W1 hard floor). Report so the operator can see the conflict.
        if cost is not None and target < round(float(cost), 2):
            skip_below_cost += 1
            report_lines.append(f"{groupid}: SKIP below_cost (Amazon lowest £{target_str} < cost £{float(cost):.2f})")
            continue

        # 3) Already matched — no DB write, no API call (the free no-op that makes repeat runs cheap).
        cur_str = f"{float(cur_price):.2f}" if cur_price is not None else None
        if cur_str == target_str:
            unchanged += 1
            continue

        # 4) A real change. (rrp is informational — above-RRP is allowed, like W1; just note it.)
        above_rrp = rrp is not None and target > round(float(rrp), 2)
        flag = " [ABOVE_RRP]" if above_rrp else ""
        old_disp = f"£{cur_str}" if cur_str else "£?"
        line = f"{groupid}: {old_disp} -> £{target_str}{flag}" + ("" if live else " (not live on Shopify)")

        if args.dry_run:
            changed += 1
            report_lines.append("WOULD CHANGE " + line)
            log("WOULD CHANGE " + line)
            continue

        # --- Write (mirrors bcweb W1): update price + audit row, commit, THEN push outward. ---------------------------
        rrp_str = f"{float(rrp):.2f}" if rrp is not None else None
        note = f"Auto-matched Amazon lowest in-stock £{target_str}"
        try:
            cur.execute("UPDATE skusummary SET shopifyprice = %s WHERE groupid = %s", (target_str, groupid))
            cur.execute(
                """
                INSERT INTO price_change_log (groupid, channel, old_price, new_price, reason_code, reason_notes, changed_by)
                VALUES (%s, 'SHP', %s, %s, NULL, %s, %s)
                """,
                (groupid, (float(cur_price) if cur_price is not None else None), target, note, CHANGED_BY)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            log(f"{groupid}: DB write FAILED — {e} (skipped, no push)")
            report_lines.append(f"{groupid}: ERROR db_write ({e})")
            continue

        changed += 1
        log("CHANGED " + line)
        report_lines.append("CHANGED " + line)

        # Push to Shopify (only if the style is live). On failure, set shopifychange=1 so the nightly price_update.py
        # sweep re-pushes it — there is no operator watching to re-Apply on an automated run.
        if live == 1:
            ok, pushed, failed = push_shopify_style(cur, groupid, target_str, rrp_str)
            if not ok:
                push_shopify_fail += 1
                try:
                    cur.execute("UPDATE skusummary SET shopifychange = 1 WHERE groupid = %s", (groupid,))
                    conn.commit()
                    log(f"  {groupid}: Shopify push incomplete ({pushed} ok / {failed} failed) — flagged shopifychange=1 for the nightly sweep")
                except Exception as e:
                    conn.rollback()
                    log(f"  {groupid}: failed to set shopifychange fallback — {e}")

    cur.close()
    conn.close()

    elapsed = time.time() - started
    summary = (f"=== amz_match_sync done ({mode}) — flagged: {len(rows)}, changed: {changed}, "
               f"unchanged: {unchanged}, no_amazon_stock: {skip_no_stock}, below_cost: {skip_below_cost}, "
               f"shopify_push_failures: {push_shopify_fail}, {elapsed:.1f}s ===")
    log(summary)
    for ln in report_lines:
        log("  " + ln)


if __name__ == "__main__":
    main()
