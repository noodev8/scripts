"""
SEO: Snapshot Google index state for every Shopify collection into Postgres.

Stores only what the GSC URL Inspection API cannot give us retroactively:
index status, referring URLs (orphan detection), and last crawl time. Google
keeps no history of these, so a page's indexing timeline is unrecoverable
unless we snapshot it. Traffic (clicks/impressions/position) is deliberately
NOT stored here -- pull it live from the Search Analytics API instead, which
serves 16 months on demand.

Runs weekly via cron on the VPS. Index state does not move hour to hour.

Inspection results are written to a dated JSON file before the DB write is
attempted: the API pass is slow and rate-limited, so a transient DB failure
must not throw it away. Recover with --load-from instead of re-inspecting.

USAGE:
• python snapshot_index_state.py
• python snapshot_index_state.py --load-from index_state_2026-07-16.json
"""

import argparse
import datetime
import json
import os
import sys
import time

import psycopg2
from googleapiclient.errors import HttpError
from psycopg2.extras import execute_values

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gsc_client import get_service, SITE_URL
from list_collections import list_collections
from logging_utils import create_logger, get_db_config, manage_log_files

SCRIPT_NAME = "snapshot_index_state"
manage_log_files(SCRIPT_NAME)
_log_to_file = create_logger(SCRIPT_NAME)

SNAPSHOT_DATE = datetime.date.today()
RESULTS_DIR = os.path.dirname(os.path.abspath(__file__))

# The URL Inspection API allows 600 queries/min and 2000/day per property, and
# each call takes a few seconds server-side anyway. The 2026-07-16 baseline ran
# all 84 collections at these settings with zero errors.
PAUSE_SECONDS = 0.15
MAX_RETRIES = 3

UPSERT_SQL = """
INSERT INTO seo_index_state
    (snapshot_date, handle, url, products_count, verdict, coverage_state,
     indexing_state, robots_txt_state, page_fetch_state, google_canonical,
     user_canonical, last_crawl_time, referring_urls, referring_url_count,
     sitemaps, inspect_error)
VALUES %s
ON CONFLICT (handle, snapshot_date) DO UPDATE SET
    url                 = EXCLUDED.url,
    products_count      = EXCLUDED.products_count,
    verdict             = EXCLUDED.verdict,
    coverage_state      = EXCLUDED.coverage_state,
    indexing_state      = EXCLUDED.indexing_state,
    robots_txt_state    = EXCLUDED.robots_txt_state,
    page_fetch_state    = EXCLUDED.page_fetch_state,
    google_canonical    = EXCLUDED.google_canonical,
    user_canonical      = EXCLUDED.user_canonical,
    last_crawl_time     = EXCLUDED.last_crawl_time,
    referring_urls      = EXCLUDED.referring_urls,
    referring_url_count = EXCLUDED.referring_url_count,
    sitemaps            = EXCLUDED.sitemaps,
    inspect_error       = EXCLUDED.inspect_error
"""


def log(message):
    """Log to file always; echo to stdout only when run by hand.

    Under cron there is no TTY, so a normal run stays silent and out of the VPS
    mail spool (crontab.txt redirects nothing). Tracebacks still surface: they
    go to stderr, which cron does mail.
    """
    _log_to_file(message)
    if sys.stdout.isatty():
        print(message, flush=True)


def inspect_url(service, url):
    """Inspect one URL, retrying on transient errors. Returns (status, error)."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = service.urlInspection().index().inspect(
                body={"inspectionUrl": url, "siteUrl": SITE_URL}
            ).execute()
            return resp["inspectionResult"].get("indexStatusResult", {}), None
        except HttpError as e:
            last_error = f"HTTP {e.resp.status}: {str(e)[:300]}"
            if e.resp.status in (429, 500, 502, 503) and attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            return {}, last_error
        except Exception as e:
            return {}, f"{type(e).__name__}: {str(e)[:300]}"
    return {}, last_error or "exhausted retries"


def build_rows():
    service = get_service()
    collections = list_collections()
    log(f"Inspecting {len(collections)} collections for {SNAPSHOT_DATE}")

    rows = []
    for n, c in enumerate(collections, 1):
        handle = c["handle"]
        url = f"{SITE_URL.rstrip('/')}/collections/{handle}"
        status, error = inspect_url(service, url)

        referring = status.get("referringUrls") or []
        rows.append((
            SNAPSHOT_DATE,
            handle,
            url,
            c["productsCount"]["count"],
            status.get("verdict"),
            status.get("coverageState"),
            status.get("indexingState"),
            status.get("robotsTxtState"),
            status.get("pageFetchState"),
            status.get("googleCanonical"),
            status.get("userCanonical"),
            status.get("lastCrawlTime"),
            referring,
            len(referring),
            status.get("sitemap") or [],
            error,
        ))

        flag = error if error else (status.get("coverageState") or "?")
        orphan = "  ORPHAN" if not referring and not error else ""
        log(f"  [{n:>3}/{len(collections)}] {handle[:44]:44} {flag[:60]}{orphan}")
        time.sleep(PAUSE_SECONDS)

    return rows


def save_rows(rows):
    path = os.path.join(RESULTS_DIR, f"index_state_{SNAPSHOT_DATE}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([list(r) for r in rows], f, indent=1, default=str)
    log(f"Saved {len(rows)} inspection results -> {path}")
    return path


def load_rows(path):
    with open(path, encoding="utf-8") as f:
        return [tuple(r) for r in json.load(f)]


def write_rows(rows):
    conn = psycopg2.connect(**get_db_config(), connect_timeout=15)
    try:
        with conn.cursor() as cur:
            execute_values(cur, UPSERT_SQL, rows)
        conn.commit()
        log(f"Upserted {len(rows)} rows into seo_index_state for {SNAPSHOT_DATE}")
    finally:
        conn.close()


def summarise(rows):
    errors = [r for r in rows if r[15]]
    log(f"--- snapshot {SNAPSHOT_DATE}: {len(rows)} collections, {len(errors)} errors ---")

    by_state = {}
    for r in rows:
        by_state.setdefault(r[5] or ("ERROR" if r[15] else "unknown"), []).append(r)
    for state, group in sorted(by_state.items(), key=lambda kv: -len(kv[1])):
        log(f"  {len(group):>3}  {state}")

    orphans = [r for r in rows if r[13] == 0 and not r[15]]
    log(f"{len(orphans)} orphaned (nothing links to them):")
    for r in sorted(orphans, key=lambda r: -(r[3] or 0)):
        log(f"      {r[1][:44]:44} {r[3]:>4} products  {r[5] or '?'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--load-from", metavar="FILE",
                    help="load a saved JSON into the DB, no API calls")
    args = ap.parse_args()

    if args.load_from:
        rows = load_rows(args.load_from)
        summarise(rows)
        write_rows(rows)
        sys.exit(0)

    rows = build_rows()
    save_rows(rows)
    summarise(rows)
    write_rows(rows)
