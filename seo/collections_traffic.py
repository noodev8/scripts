"""
SEO: Merge Shopify collections with Search Console traffic (last 90 days).

Pulls clicks/impressions/position per page from GSC, filters to /collections/
URLs, and joins onto collections.csv (run export_collections_csv.py first).
"""

import csv
import datetime
import os
from gsc_client import get_service, SITE_URL

SCRIPT_DIR = os.path.dirname(__file__)
COLLECTIONS_CSV = os.path.join(SCRIPT_DIR, "collections.csv")
OUT_PATH = os.path.join(SCRIPT_DIR, "collections_with_traffic.csv")

DAYS = 90


def fetch_page_traffic():
    service = get_service()
    end = datetime.date.today() - datetime.timedelta(days=3)  # GSC data lags a few days
    start = end - datetime.timedelta(days=DAYS)

    rows = []
    start_row = 0
    while True:
        body = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["page"],
            "rowLimit": 25000,
            "startRow": start_row,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
        batch = resp.get("rows", [])
        rows.extend(batch)
        if len(batch) < 25000:
            break
        start_row += 25000

    # keys[0] = page URL
    traffic = {}
    for r in rows:
        page = r["keys"][0]
        traffic[page] = {
            "clicks": r["clicks"],
            "impressions": r["impressions"],
            "position": round(r["position"], 1),
        }
    return traffic


if __name__ == "__main__":
    traffic = fetch_page_traffic()
    print(f"Fetched traffic for {len(traffic)} pages total (last {DAYS} days)")

    with open(COLLECTIONS_CSV, encoding="utf-8") as f:
        collections = list(csv.DictReader(f))

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "handle", "products_count", "url", "clicks", "impressions", "position"])
        matched = 0
        for c in collections:
            url = f"{SITE_URL.rstrip('/')}/collections/{c['handle']}"
            t = traffic.get(url)
            if t:
                matched += 1
            writer.writerow([
                c["title"], c["handle"], c["products_count"], url,
                t["clicks"] if t else 0,
                t["impressions"] if t else 0,
                t["position"] if t else "",
            ])

    print(f"Matched traffic for {matched}/{len(collections)} collections")
    print(f"Wrote {OUT_PATH}")
