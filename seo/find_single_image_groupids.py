"""
find_single_image_groupids.py — one-off audit.

Lists every Shopify groupid that has fewer than 2 images live on Shopify.

This queries the Shopify Admin GraphQL API directly (the authoritative source),
NOT the `shopifyimages` DB table — that table only holds handles the nightly
updateimages.py job has touched (0/1-row handles inside a date window), so it
can't tell "genuinely single-image" apart from "never synced".

Mapping is skusummary.handle -> groupid where shopify = 1.

Usage:
    python find_single_image_groupids.py [--min N] [--csv out.csv]

    --min N   flag groupids with fewer than N images (default 2)
    --csv     also write the results to a CSV (groupid, handle, images)
"""

import os
import sys
import csv
import time
import argparse

import requests
import psycopg2

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)
from dotenv import load_dotenv
from logging_utils import get_db_config

load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
GRAPHQL_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"

IMAGE_QUERY = """
query($query: String!) {
    products(first: 100, query: $query) {
        edges {
            node {
                handle
                images(first: 20) {
                    edges { node { url } }
                }
            }
        }
    }
}
"""


def get_shopify_groupids():
    """{handle: groupid} for every active Shopify product with a handle."""
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT handle, groupid
        FROM skusummary
        WHERE shopify = 1 AND handle IS NOT NULL AND handle != ''
    """)
    mapping = {handle: groupid for handle, groupid in cur.fetchall()}
    cur.close()
    conn.close()
    return mapping


def fetch_image_counts(handles, batch_size=25):
    """{handle: image_count} from Shopify. Handles not returned are omitted."""
    counts = {}
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json",
    }

    total = len(handles)
    for i in range(0, total, batch_size):
        batch = handles[i:i + batch_size]
        handle_query = " OR ".join(f"handle:{h}" for h in batch)
        payload = {"query": IMAGE_QUERY, "variables": {"query": handle_query}}

        r = requests.post(GRAPHQL_URL, json=payload, headers=headers)
        if r.status_code == 429:
            print("Rate limited, waiting 5s...")
            time.sleep(5)
            r = requests.post(GRAPHQL_URL, json=payload, headers=headers)
        if r.status_code != 200:
            print(f"  ! batch {i}-{i + len(batch)} failed: HTTP {r.status_code}")
            continue

        data = r.json()
        if "errors" in data:
            print(f"  ! GraphQL errors: {data['errors']}")
            continue

        edges = data.get("data", {}).get("products", {}).get("edges", [])
        for edge in edges:
            node = edge["node"]
            handle = node["handle"]
            if handle in batch:
                counts[handle] = len(node["images"]["edges"])

        print(f"  ...{min(i + batch_size, total)}/{total} handles")
        time.sleep(1.0)

    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=2,
                    help="flag groupids with fewer than this many images (default 2)")
    ap.add_argument("--csv", help="also write results to this CSV path")
    args = ap.parse_args()

    mapping = get_shopify_groupids()
    handles = list(mapping.keys())
    print(f"{len(handles)} active Shopify handles to check.\n")

    counts = fetch_image_counts(handles)

    # Collapse handle -> groupid. A groupid can in theory span >1 handle;
    # take the max image count seen across its handles so we don't false-flag.
    by_groupid = {}
    for handle, groupid in mapping.items():
        n = counts.get(handle)  # None = Shopify didn't return it (treat as 0)
        n = 0 if n is None else n
        prev = by_groupid.get(groupid)
        if prev is None or n > prev[0]:
            by_groupid[groupid] = (n, handle)

    flagged = sorted(
        ((gid, n, handle) for gid, (n, handle) in by_groupid.items() if n < args.min),
        key=lambda x: (x[1], x[0]),
    )

    print(f"\n{len(flagged)} groupid(s) with fewer than {args.min} image(s):\n")
    print(f"{'groupid':<20} {'images':>6}  handle")
    print("-" * 60)
    for gid, n, handle in flagged:
        print(f"{gid:<20} {n:>6}  {handle}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["groupid", "images", "handle"])
            w.writerows(flagged)
        print(f"\nWrote {len(flagged)} rows to {args.csv}")


if __name__ == "__main__":
    main()
