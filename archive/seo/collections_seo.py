"""
SEO: every Shopify collection with its Search Console position and clicks.

Shopify knows what collections exist; GSC knows which ones Google shows anyone.
Neither alone answers "which collections are invisible" -- GSC only returns
pages that earned an impression, so a collection missing from GSC entirely does
not show up as a zero, it just isn't there. This joins the two, so collections
earning nothing appear as rows rather than absences.

28d window: a single collection does ~6 clicks/week, where 7d is pure noise.

USAGE:
• python collections.py
• python collections.py --unranked       (only collections earning no clicks)
• python collections.py --top 40         (rows, default all)
"""

import argparse
import datetime
import os
import sys

import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from gsc_client import get_service, SITE_URL

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
GSC_LAG_DAYS = 3
WINDOW_DAYS = 28
SITE_ROOT = SITE_URL.rstrip("/")


def shopify_collections():
    token = os.getenv("SHOPIFY_ACCESS_TOKEN")
    if not token:
        raise ValueError("SHOPIFY_ACCESS_TOKEN not found in .env file")

    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    query = """
    query($cursor: String) {
        collections(first: 50, after: $cursor) {
            edges {
                node {
                    title
                    handle
                    productsCount { count }
                    seo { title description }
                }
            }
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


def gsc_by_handle(start, end):
    """GSC rows for /collections/ pages, keyed by handle."""
    service = get_service()
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["page"],
        "rowLimit": 25000,
    }
    rows = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute().get("rows", [])
    out = {}
    for r in rows:
        url = r["keys"][0]
        if "/collections/" not in url:
            continue
        # Strip query strings and trailing paths so ?page=2 folds into the handle.
        handle = url.split("/collections/")[1].split("?")[0].split("/")[0].rstrip("/")
        if handle not in out:
            out[handle] = {"clicks": 0, "impressions": 0, "pos_weight": 0}
        out[handle]["clicks"] += r["clicks"]
        out[handle]["impressions"] += r["impressions"]
        out[handle]["pos_weight"] += r["position"] * r["impressions"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unranked", action="store_true", help="only collections earning no clicks")
    ap.add_argument("--top", type=int, help="rows (default all)")
    args = ap.parse_args()

    end = datetime.date.today() - datetime.timedelta(days=GSC_LAG_DAYS)
    start = end - datetime.timedelta(days=WINDOW_DAYS - 1)

    cols = shopify_collections()
    gsc = gsc_by_handle(start, end)

    rows = []
    for c in cols:
        g = gsc.get(c["handle"])
        clicks = g["clicks"] if g else 0
        impr = g["impressions"] if g else 0
        # Impression-weighted: a plain mean lets a page with 3 impressions at
        # position 90 drag the number around.
        pos = (g["pos_weight"] / impr) if g and impr else 0
        rows.append({
            "handle": c["handle"],
            "products": c["productsCount"]["count"],
            "clicks": clicks,
            "impressions": impr,
            "ctr": clicks / impr * 100 if impr else 0,
            "pos": pos,
            "seo_title": bool(c["seo"]["title"]),
        })

    if args.unranked:
        rows = [r for r in rows if r["clicks"] == 0]
    rows.sort(key=lambda r: (-r["clicks"], -r["impressions"]))
    shown = rows[:args.top] if args.top else rows

    total_clicks = sum(r["clicks"] for r in rows)
    print(f"\nCOLLECTIONS - {WINDOW_DAYS}d to {end} - {len(cols)} in Shopify, "
          f"{len(gsc)} seen by Google\n")
    print("=" * 78)
    print(f"  {'collection':38} {'prods':>5} {'clicks':>6} {'impr':>8} {'CTR':>6} "
          f"{'pos':>5} {'seo':>4}")
    print("=" * 78)
    for r in shown:
        pos = f"{r['pos']:>5.1f}" if r["pos"] else "    -"
        print(f"  {r['handle'][:38]:38} {r['products']:>5} {r['clicks']:>6,.0f} "
              f"{r['impressions']:>8,.0f} {r['ctr']:>5.2f}% {pos} "
              f"{'y' if r['seo_title'] else '-':>4}")

    dead = [r for r in rows if r["clicks"] == 0]
    print(f"\n  {len(shown)} shown, {total_clicks:,.0f} clicks. "
          f"{len(dead)} collections earn nothing.")
    print("  'seo' = a custom SEO title is set in Shopify. 'pos' blank = no impressions.\n")


if __name__ == "__main__":
    main()
