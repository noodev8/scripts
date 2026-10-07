#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shopify product descriptions for the Google Merchant feed - reviewed weekly.

The nightly feed sends only descriptions a person has approved
(shopify_description.description); anything not yet approved goes out with the
title, as before. It never calls Shopify and never cleans anything itself.

The weekly review is done with Claude:

    python merchant-feed/descriptions.py review             # fetch from Shopify, list new/changed
    python merchant-feed/descriptions.py approve --all      # approve every proposal in the list
    python merchant-feed/descriptions.py approve 0128161-MADRID 1005291-ARIZONA
    python merchant-feed/descriptions.py approve 0128161-MADRID --text "Hand-written text"

`review` fetches every product's HTML (two GraphQL calls for the whole
catalogue), cleans it, and lists the feed products that are new or whose Shopify
HTML has changed since approval, with the proposed text and any risky words
still in it. The full list is written to merchant-feed/logs/description_review.md.

Cleaning removes website navigation, delivery promises, emoji and embedded
CSS/images. The "Stock Code: ..." line is kept on purpose - shoppers search by
style code.
"""

import os
import re
import sys
import html
from html.parser import HTMLParser

import requests
import psycopg2
from psycopg2.extras import execute_values

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, ".."))
from dotenv import load_dotenv
from logging_utils import get_db_config

load_dotenv(dotenv_path=os.path.join(SCRIPT_DIR, "..", ".env"))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"

# Below this many characters (ignoring the stock code) a description says
# nothing the title doesn't, so the feed falls back to the title.
MIN_USEFUL_LENGTH = 40
GOOGLE_MAX_LENGTH = 5000

BLOCK_TAGS = {"p", "li", "div", "br", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "table"}
SKIP_TAGS = {"style", "script", "svg"}

# A block containing a link is navigation ("Width Options REGULAR / NARROW",
# "View all Arizona sandals here") unless it carries this much other text.
NAV_BLOCK_MAX = 60

REMOVE_PATTERNS = [
    # Delivery promises - Google disallows shipping/promo claims in descriptions.
    # Worded many ways ("Order by 2pm Mon - Fri for NEXT DAY delivery...", "This
    # item can be picked SAME DAY..."), so drop any sentence that makes one.
    r"[^.!?]*\b(?:next day|same day|24 ?hr) (?:delivery|pick)[^.!?]*(?:[.!?]|$)",
    r"[^.!?]*\bdelivery option available[^.!?]*(?:[.!?]|$)",
    # Link lead-ins left behind when the link text sits mid-paragraph
    r"(?:View|See) all [A-Za-z ]+? sandals",
    r"(?:Width|Colour) Options",
]
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")


class _Blocks(HTMLParser):
    """Splits description HTML into text blocks, tracking link text separately."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self._text, self._link = [], []
        self._skip = 0
        self._in_link = 0

    def _flush(self):
        text = " ".join("".join(self._text).split())
        link = "".join(self._link).strip()
        if text and not (link and len(text) < NAV_BLOCK_MAX):
            self.blocks.append(text)
        self._text, self._link = [], []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self._skip += 1
        elif tag == "a":
            self._in_link += 1
        elif tag in BLOCK_TAGS:
            self._flush()

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
        elif tag == "a":
            self._in_link = max(0, self._in_link - 1)
        elif tag in BLOCK_TAGS:
            self._flush()

    def handle_data(self, data):
        if self._skip:
            return
        (self._link if self._in_link else self._text).append(data)

    def close(self):
        super().close()
        self._flush()


def clean(description_html):
    """Plain-text description for Google, or '' if there's nothing worth sending."""
    if not description_html:
        return ""
    parser = _Blocks()
    parser.feed(html.unescape(description_html) if "&lt;" in description_html else description_html)
    parser.close()

    blocks = []
    for block in parser.blocks:
        block = EMOJI.sub("", block.replace("﻿", "").replace("\xa0", " "))
        for pattern in REMOVE_PATTERNS:
            block = re.sub(pattern, "", block, flags=re.IGNORECASE)
        block = " ".join(block.split()).strip(" -|")
        if block:
            # Keep list items readable once the line breaks are gone
            blocks.append(block if block[-1] in ".!?:;" else block + ".")

    text = " ".join(blocks)
    return text[:GOOGLE_MAX_LENGTH].rsplit(" ", 1)[0] if len(text) > GOOGLE_MAX_LENGTH else text


def feed_description(description_html, title):
    """What goes in the feed's description column: cleaned text, else the title."""
    text = clean(description_html)
    stock_code = re.search(r"Stock Code:\s*\S+", text)
    body = text.replace(stock_code.group(0), "") if stock_code else text
    if len(body.strip(" .")) >= MIN_USEFUL_LENGTH:
        return text
    # Too thin to beat the title - but keep the stock code searchable
    return f"{title}. {stock_code.group(0)}" if stock_code else title


def refresh(conn, log=print):
    """Upsert every Shopify product's descriptionHtml. Returns rows written."""
    token = os.getenv("SHOPIFY_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("SHOPIFY_ACCESS_TOKEN not found in .env")
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
    query = """query($cursor: String) {
        products(first: 250, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            nodes { handle updatedAt descriptionHtml }
        }
    }"""

    rows, cursor, calls = [], None, 0
    while True:
        r = requests.post(url, json={"query": query, "variables": {"cursor": cursor}},
                          headers={"X-Shopify-Access-Token": token}, timeout=60)
        r.raise_for_status()
        payload = r.json()
        if payload.get("errors"):
            raise RuntimeError(f"Shopify GraphQL errors: {payload['errors']}")
        calls += 1
        page = payload["data"]["products"]
        rows += [(n["handle"], n["descriptionHtml"], n["updatedAt"]) for n in page["nodes"]]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO shopify_description (handle, description_html, shopify_updated_at, fetched_at)
            VALUES %s
            ON CONFLICT (handle) DO UPDATE SET
                description_html = EXCLUDED.description_html,
                shopify_updated_at = EXCLUDED.shopify_updated_at,
                fetched_at = EXCLUDED.fetched_at
        """, rows, template="(%s, %s, %s, now())")
    conn.commit()
    log(f"Descriptions refreshed: {len(rows)} products in {calls} Shopify call(s)")
    return len(rows)


RISKY = re.compile(r"\b(?:deliver\w*|dispatch\w*|free|returns?|sale|% off|discount\w*|click|here|order by|next day|same day|24 ?hr)\b", re.IGNORECASE)

PENDING_SQL = """
    SELECT DISTINCT sm.groupid, t.shopifytitle, sd.handle, sd.description_html,
           sd.approved_at IS NOT NULL AS was_approved
    FROM skusummary sm
    JOIN skumap m ON m.groupid = sm.groupid
    LEFT JOIN title t ON t.groupid = sm.groupid
    JOIN shopify_description sd ON sd.handle = sm.handle
    WHERE sm.googlestatus = 1 AND sm.shopify = 1 AND m.googlestatus = 1
      AND sd.approved_html IS DISTINCT FROM sd.description_html
    ORDER BY sm.groupid
"""


def _pending(conn):
    with conn.cursor() as cur:
        cur.execute(PENDING_SQL)
        return [dict(zip(("groupid", "title", "handle", "html", "was_approved"), r)) for r in cur.fetchall()]


def review(conn):
    pending = _pending(conn)
    lines, flagged = [], 0
    for p in pending:
        text = feed_description(p["html"], p["title"])
        risky = sorted({m.group(0).lower() for m in RISKY.finditer(text)})
        flagged += bool(risky)
        status = "CHANGED" if p["was_approved"] else "NEW"
        lines.append(f"### {p['groupid']} - {status}" + (f" - CHECK: {', '.join(risky)}" if risky else ""))
        lines.append(text + "\n")
    path = os.path.join(SCRIPT_DIR, "logs", "description_review.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Description review - {len(pending)} to approve, {flagged} with words to check\n\n")
        f.write("\n".join(lines))
    print(f"{len(pending)} new/changed feed products, {flagged} with words to check")
    print(f"Proposals written to {path}")


def approve(conn, groupids, text=None):
    pending = _pending(conn)
    if groupids:
        wanted = set(groupids)
        missing = wanted - {p["groupid"] for p in pending}
        if missing:
            raise SystemExit(f"Not pending review (unknown, or already approved): {', '.join(sorted(missing))}")
        pending = [p for p in pending if p["groupid"] in wanted]
    if text is not None and len(pending) != 1:
        raise SystemExit("--text needs exactly one groupid")

    with conn.cursor() as cur:
        for p in pending:
            final = " ".join(text.split()) if text is not None else feed_description(p["html"], p["title"])
            # approved_html records which Shopify version was reviewed, so a later
            # edit in Shopify shows up as CHANGED in the next review
            cur.execute("""
                UPDATE shopify_description
                SET description = %s, approved_html = description_html, approved_at = now()
                WHERE handle = %s
            """, (final, p["handle"]))
    conn.commit()
    print(f"Approved {len(pending)} description(s)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Weekly review of Shopify descriptions for the merchant feed")
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("review", help="Fetch from Shopify and list new/changed descriptions")
    r.add_argument("--no-fetch", action="store_true", help="Skip the Shopify fetch; review stored HTML")
    a = sub.add_parser("approve", help="Approve proposals so the nightly feed sends them")
    a.add_argument("groupids", nargs="*")
    a.add_argument("--all", action="store_true", help="Approve everything pending review")
    a.add_argument("--text", help="Hand-written description for a single groupid")
    args = parser.parse_args()

    if args.command == "approve" and not (args.groupids or args.all):
        parser.error("approve needs groupids or --all")

    conn = psycopg2.connect(**get_db_config())
    try:
        if args.command == "review":
            if not args.no_fetch:
                refresh(conn)
            review(conn)
        else:
            approve(conn, args.groupids, args.text)
    finally:
        conn.close()
