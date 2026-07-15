#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keep images in sync for the newest skusummary rows, ahead of full PowerBuilder
replacement:

1. LOCAL IMAGE SYNC — reads C:/brookfieldcomfort/brookfield.ini for the
   "dropbox" path, and downloads any missing main image from
   https://images.brookfieldcomfort.com/{imagename} into
   {dropbox}\\assets\\images\\ for the last N products loaded to skusummary.

2. SHOPIFY EXTRA-IMAGE SYNC — replaces the old "export CSV, strip Body column,
   run PowerBuilder function" workflow. Extra images uploaded directly in the
   Shopify UI never make it into skusummary (which only tracks the single main
   image), so they used to get lost from our database. For the same last N
   products, checks the `shopifyimages` table (handle, imagepos, imagesrc)
   first — only handles with 0 or 1 rows there are queried against the
   Shopify Admin API, to avoid needlessly hitting the API for products we
   already know have multiple images recorded.

Run ad-hoc: python updateimages.py [--limit 50] [--dry-run]
"""

import os
import sys
import time
import argparse
import requests
import psycopg2

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from dotenv import load_dotenv
from logging_utils import get_db_config, manage_log_files, create_logger

load_dotenv(dotenv_path=os.path.join(SCRIPT_DIR, ".env"))

SCRIPT_NAME = "updateimages"
manage_log_files(SCRIPT_NAME)
log = create_logger(SCRIPT_NAME)

INI_PATH = r"C:\brookfieldcomfort\brookfield.ini"
IMAGE_BASE_URL = "https://images.brookfieldcomfort.com/"

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
GRAPHQL_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"


def get_dropbox_path():
    """Parse the 'dropbox=' line out of brookfield.ini (plain key=value, no section headers)."""
    if not os.path.exists(INI_PATH):
        raise FileNotFoundError(f"Could not find {INI_PATH}")

    with open(INI_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith("dropbox="):
                return line.split("=", 1)[1].strip()

    raise ValueError(f"No 'dropbox=' line found in {INI_PATH}")


def get_recent_products(limit):
    """Last N skusummary rows by created date: groupid, imagename, handle."""
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        SELECT groupid, imagename, handle, created
        FROM skusummary
        WHERE imagename IS NOT NULL AND imagename != ''
        ORDER BY created DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def sync_local_images(rows, images_dir, dry_run=False):
    checked = 0
    already_present = 0
    downloaded = 0
    failed = 0

    for groupid, imagename, handle, created in rows:
        checked += 1
        local_path = os.path.join(images_dir, imagename)

        if os.path.exists(local_path):
            already_present += 1
            continue

        if dry_run:
            log(f"[DRY RUN] Would download {imagename} (groupid={groupid}, created={created})")
            downloaded += 1
            continue

        url = IMAGE_BASE_URL + imagename
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(resp.content)
            downloaded += 1
            log(f"Downloaded {imagename} (groupid={groupid})")
        except Exception as e:
            failed += 1
            log(f"FAILED {imagename} (groupid={groupid}): {e}")

    log(f"Local images — checked: {checked}, already present: {already_present}, "
        f"downloaded: {downloaded}, failed: {failed}")


def get_handles_needing_check(handles):
    """Return the subset of handles that have 0 or 1 rows in shopifyimages."""
    if not handles:
        return []

    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        SELECT handle, COUNT(*)
        FROM shopifyimages
        WHERE handle = ANY(%s)
        GROUP BY handle
    """, (handles,))
    counts = dict(cur.fetchall())
    cur.close()
    conn.close()

    return [h for h in handles if counts.get(h, 0) <= 1]


def fetch_shopify_images(handles, batch_size=25):
    """
    Query Shopify GraphQL for product images by handle, in batches.
    Returns dict: {handle: [imagesrc, imagesrc, ...]} in Shopify's image order.
    """
    results = {}
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    query = """
    query($query: String!) {
        products(first: 100, query: $query) {
            edges {
                node {
                    handle
                    images(first: 20) {
                        edges {
                            node {
                                url
                            }
                        }
                    }
                }
            }
        }
    }
    """

    for i in range(0, len(handles), batch_size):
        batch_handles = handles[i:i + batch_size]
        handle_query = " OR ".join([f"handle:{h}" for h in batch_handles])
        payload = {"query": query, "variables": {"query": handle_query}}

        try:
            r = requests.post(GRAPHQL_URL, json=payload, headers=headers)
            if r.status_code == 429:
                log("Rate limited, waiting 5 seconds...")
                time.sleep(5)
                r = requests.post(GRAPHQL_URL, json=payload, headers=headers)

            if r.status_code != 200:
                log(f"Shopify GraphQL request failed with status {r.status_code}")
                continue

            data = r.json()
            if "errors" in data:
                log(f"GraphQL errors in image batch request: {data['errors']}")
                continue

            edges = data.get("data", {}).get("products", {}).get("edges", [])
            for edge in edges:
                node = edge["node"]
                handle = node["handle"]
                if handle in batch_handles:
                    image_urls = [img["node"]["url"] for img in node["images"]["edges"]]
                    results[handle] = image_urls

            time.sleep(1.0)

        except Exception as e:
            log(f"Exception in fetch_shopify_images: {str(e)}")
            continue

    return results


def update_shopifyimages_table(handle_images, dry_run=False):
    """Replace shopifyimages rows for each handle with the freshly fetched image list."""
    if not handle_images:
        return 0

    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    updated = 0

    for handle, image_urls in handle_images.items():
        if dry_run:
            log(f"[DRY RUN] Would refresh shopifyimages for handle={handle} ({len(image_urls)} images)")
            continue

        cur.execute("DELETE FROM shopifyimages WHERE handle = %s", (handle,))
        for pos, url in enumerate(image_urls, start=1):
            cur.execute(
                "INSERT INTO shopifyimages (handle, imagepos, imagesrc) VALUES (%s, %s, %s)",
                (handle, pos, url)
            )
        updated += 1

    if not dry_run:
        conn.commit()
    cur.close()
    conn.close()
    return updated


def sync_shopify_images(rows, dry_run=False):
    if not ACCESS_TOKEN:
        log("SHOPIFY_ACCESS_TOKEN not found in .env — skipping Shopify image sync")
        return

    handles = [handle for _, _, handle, _ in rows if handle]
    to_check = get_handles_needing_check(handles)

    log(f"Shopify images — {len(handles)} handles in window, {len(to_check)} need an API check "
        f"(0 or 1 rows in shopifyimages)")

    if not to_check:
        return

    handle_images = fetch_shopify_images(to_check)
    updated = update_shopifyimages_table(handle_images, dry_run=dry_run)
    log(f"Shopify images — refreshed {updated} handle(s) in shopifyimages")


def get_all_active_handles():
    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        SELECT handle FROM skusummary
        WHERE handle IS NOT NULL AND handle != '' AND shopify = 1
    """)
    handles = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return handles


def full_resync_shopify_images(dry_run=False):
    """
    One-shot bootstrap: wipe shopifyimages and rebuild it from the Shopify API
    for every active product, bypassing the 0/1-row gate used on normal runs.
    Use this once to recover from a CSV import overwriting UI-added images, or
    to seed the table before relying on the incremental last-N sync.
    """
    if not ACCESS_TOKEN:
        log("SHOPIFY_ACCESS_TOKEN not found in .env — cannot run full resync")
        return

    handles = get_all_active_handles()
    log(f"=== FULL SHOPIFY IMAGE RESYNC STARTED ({len(handles)} active handles) ===")

    if not dry_run:
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE shopifyimages")
        conn.commit()
        cur.close()
        conn.close()
        log("Truncated shopifyimages")
    else:
        log("[DRY RUN] Would truncate shopifyimages")

    handle_images = fetch_shopify_images(handles)
    updated = update_shopifyimages_table(handle_images, dry_run=dry_run)
    log(f"Full resync — refreshed {updated} of {len(handles)} handle(s)")
    log("=== FULL SHOPIFY IMAGE RESYNC COMPLETED ===")


def sync_images(limit=50, dry_run=False):
    dropbox_path = get_dropbox_path()
    images_dir = os.path.join(dropbox_path, "assets", "images")

    if not os.path.isdir(images_dir):
        raise FileNotFoundError(f"Images folder not found: {images_dir}")

    rows = get_recent_products(limit)
    log(f"=== IMAGE SYNC STARTED (checking last {limit} new products) ===")
    log(f"Target folder: {images_dir}")

    sync_local_images(rows, images_dir, dry_run=dry_run)
    sync_shopify_images(rows, dry_run=dry_run)

    log("=== IMAGE SYNC COMPLETED ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync missing product images (local Drive + Shopify extra images)")
    parser.add_argument("--limit", type=int, default=50, help="Number of most recently created skusummary rows to check (default 50)")
    parser.add_argument("--dry-run", action="store_true", help="List what would change without downloading or writing to the DB")
    parser.add_argument("--full", action="store_true", help="One-shot: wipe and rebuild shopifyimages for ALL active products from the Shopify API")
    args = parser.parse_args()

    if args.full:
        full_resync_shopify_images(dry_run=args.dry_run)
    else:
        sync_images(limit=args.limit, dry_run=args.dry_run)
