"""
SEO hygiene: Shopify collections sorted by how few products they hold.

An empty or near-empty collection is a bad page regardless of clicks -- thin
content, looks broken to visitors and Google, wastes crawl budget. This is the
delete-candidate finder. Product count is the signal, not clicks.

Two things flagged so we do not delete something we should keep:
- SMART collections (rule-based) can be empty *now* but refill seasonally. An
  empty MANUAL collection is a real dead page; an empty smart one may be off-season.
- 'seo' = a custom SEO title is set (someone invested in the page once).

Deleting still needs the link check + a 301 redirect (see chat) -- this only
finds the candidates.

USAGE:
• python thin_collections.py                (all, thinnest first)
• python thin_collections.py --max 3        (only collections with <= 3 products)
"""

import argparse
import os
import sys

import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"


def collections():
    token = os.getenv("SHOPIFY_ACCESS_TOKEN")
    if not token:
        raise ValueError("SHOPIFY_ACCESS_TOKEN not found in .env")
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    query = """
    query($cursor: String) {
        collections(first: 50, after: $cursor) {
            edges { node {
                title handle
                productsCount { count }
                ruleSet { rules { column } }
                seo { title }
            } }
            pageInfo { hasNextPage endCursor }
        }
    }
    """
    out, cursor = [], None
    while True:
        resp = requests.post(url, headers=headers,
                             json={"query": query, "variables": {"cursor": cursor}})
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(data["errors"])
        block = data["data"]["collections"]
        out.extend(e["node"] for e in block["edges"])
        if not block["pageInfo"]["hasNextPage"]:
            return out
        cursor = block["pageInfo"]["endCursor"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=None,
                    help="only collections with <= this many products")
    args = ap.parse_args()

    cols = collections()
    rows = [{
        "handle": c["handle"],
        "n": c["productsCount"]["count"],
        "smart": c["ruleSet"] is not None,
        "seo": bool(c["seo"]["title"]),
    } for c in cols]
    rows.sort(key=lambda r: (r["n"], r["handle"]))
    if args.max is not None:
        rows = [r for r in rows if r["n"] <= args.max]

    print(f"\nTHIN COLLECTIONS - {len(cols)} in Shopify, thinnest first\n")
    print(f"  {'collection':42} {'prods':>5} {'type':>7} {'seo':>4}")
    print("  " + "-" * 62)
    for r in rows:
        print(f"  {r['handle'][:42]:42} {r['n']:>5} "
              f"{'smart' if r['smart'] else 'manual':>7} {'y' if r['seo'] else '-':>4}")

    empty = [r for r in rows if r["n"] == 0]
    thin = [r for r in rows if 1 <= r["n"] <= 3]
    print(f"\n  {len(empty)} empty (0 products), {len(thin)} thin (1-3). "
          f"Manual + empty = real dead page; smart + empty may be off-season.\n")


if __name__ == "__main__":
    main()
