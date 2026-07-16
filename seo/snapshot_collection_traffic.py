"""
SEO: Snapshot Shopify collections + Search Console traffic into Postgres.

Run this on a schedule (e.g. weekly/monthly) to build a trend of clicks,
impressions, and position per collection over time.

USAGE:
• python snapshot_collection_traffic.py
"""

import datetime
import os
import sys
import psycopg2
from psycopg2.extras import execute_values

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from list_collections import list_collections
from gsc_client import SITE_URL
from collections_traffic import fetch_page_traffic
from logging_utils import get_db_config

SNAPSHOT_DATE = datetime.date.today()

UPSERT_SQL = """
INSERT INTO seo_collection_traffic
    (snapshot_date, handle, title, products_count, url, seo_title, seo_description,
     clicks, impressions, position)
VALUES %s
ON CONFLICT (handle, snapshot_date) DO UPDATE SET
    title = EXCLUDED.title,
    products_count = EXCLUDED.products_count,
    url = EXCLUDED.url,
    seo_title = EXCLUDED.seo_title,
    seo_description = EXCLUDED.seo_description,
    clicks = EXCLUDED.clicks,
    impressions = EXCLUDED.impressions,
    position = EXCLUDED.position
"""


def build_rows():
    collections = list_collections()
    traffic = fetch_page_traffic()

    rows = []
    for c in collections:
        url = f"{SITE_URL.rstrip('/')}/collections/{c['handle']}"
        t = traffic.get(url)
        rows.append((
            SNAPSHOT_DATE,
            c["handle"],
            c["title"],
            c["productsCount"]["count"],
            url,
            c["seo"]["title"] or None,
            c["seo"]["description"] or None,
            t["clicks"] if t else 0,
            t["impressions"] if t else 0,
            t["position"] if t else None,
        ))
    return rows


if __name__ == "__main__":
    rows = build_rows()
    print(f"Built {len(rows)} rows for snapshot_date={SNAPSHOT_DATE}")

    db_config = get_db_config()
    conn = psycopg2.connect(**db_config)
    try:
        with conn.cursor() as cur:
            execute_values(cur, UPSERT_SQL, rows)
        conn.commit()
        print(f"Upserted {len(rows)} rows into seo_collection_traffic")
    finally:
        conn.close()
