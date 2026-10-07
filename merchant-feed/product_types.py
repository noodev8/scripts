#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product type and Google category for the merchant feed - reviewed weekly.

The nightly feed sends only what's been approved here (merchant_product_type);
an unreviewed product goes out with no product_type and category 187 (Shoes).
The feed never works these out itself.

Done alongside the description review, with Claude:

    python merchant-feed/product_types.py review           # list new/changed proposals
    python merchant-feed/product_types.py approve --all
    python merchant-feed/product_types.py approve M196A 17659-23
    python merchant-feed/product_types.py approve M196A --type "Home > Mens > Footwear > Mens Wide Fit Shoes"

Proposals come from attributes.gender and attributes.producttype. A product is
listed when it has never been approved, or when its proposal has changed since
(e.g. its producttype was edited) - approved_proposal records what was reviewed.
"""

import os
import sys

import psycopg2

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, ".."))
from dotenv import load_dotenv
from logging_utils import get_db_config

load_dotenv(dotenv_path=os.path.join(SCRIPT_DIR, "..", ".env"))

# Google product taxonomy IDs (taxonomy-with-ids.en-GB.txt)
CATEGORY_SHOES = 187   # Clothing & Accessories > Shoes
CATEGORY_SOCKS = 209   # Clothing & Accessories > Clothing > Underwear & Socks > Socks

# Every attributes.producttype of 'Accessories' in the feed is a sock. If that
# stops being true, the review shows it and the category can be overridden.
CATEGORY_BY_TYPE = {"Accessories": CATEGORY_SOCKS}


def propose(gender, producttype, title):
    """(product_type, google_category) for one groupid."""
    gender = (gender or "").strip().title()
    producttype = (producttype or "").strip().title()
    category = CATEGORY_BY_TYPE.get(producttype, CATEGORY_SHOES)
    if not gender or not producttype:
        return "", category
    if producttype == "Accessories":
        return f"Home > {gender} > Accessories", category
    fit = "Wide Fit " if "WIDE" in (title or "").upper() else ""
    return f"Home > {gender} > Footwear > {gender} {fit}{producttype}", category


def _key(product_type, category):
    return f"{product_type}|{category}"


def _pending(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT sm.groupid, a.gender, a.producttype, t.shopifytitle,
                   mpt.approved_proposal
            FROM skusummary sm
            JOIN skumap m ON m.groupid = sm.groupid
            LEFT JOIN attributes a ON a.groupid = sm.groupid
            LEFT JOIN title t ON t.groupid = sm.groupid
            LEFT JOIN merchant_product_type mpt ON mpt.groupid = sm.groupid
            WHERE sm.googlestatus = 1 AND sm.shopify = 1 AND m.googlestatus = 1
            ORDER BY sm.groupid
        """)
        rows = cur.fetchall()
    pending = []
    for groupid, gender, producttype, title, approved in rows:
        product_type, category = propose(gender, producttype, title)
        if approved != _key(product_type, category):
            pending.append({"groupid": groupid, "title": title, "product_type": product_type,
                            "category": category, "was_approved": approved is not None})
    return pending


def review(conn):
    pending = _pending(conn)
    for p in pending:
        status = "CHANGED" if p["was_approved"] else "NEW"
        warn = "  <- NO PRODUCT TYPE (check attributes)" if not p["product_type"] else ""
        print(f"{p['groupid']:<24} {status:<8} {p['category']:<4} {p['product_type']}{warn}")
    print(f"\n{len(pending)} new/changed feed products")


def approve(conn, groupids, product_type=None, category=None):
    pending = _pending(conn)
    if groupids:
        wanted = set(groupids)
        missing = wanted - {p["groupid"] for p in pending}
        if missing:
            raise SystemExit(f"Not pending review (unknown, or already approved): {', '.join(sorted(missing))}")
        pending = [p for p in pending if p["groupid"] in wanted]
    if (product_type is not None or category is not None) and not groupids:
        raise SystemExit("--type/--category need explicit groupids")

    with conn.cursor() as cur:
        for p in pending:
            cur.execute("""
                INSERT INTO merchant_product_type (groupid, product_type, google_category, approved_proposal, approved_at)
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (groupid) DO UPDATE SET
                    product_type = EXCLUDED.product_type,
                    google_category = EXCLUDED.google_category,
                    approved_proposal = EXCLUDED.approved_proposal,
                    approved_at = EXCLUDED.approved_at
            """, (p["groupid"],
                  product_type if product_type is not None else p["product_type"],
                  category if category is not None else p["category"],
                  # The proposal as reviewed, even if overridden, so the product
                  # only comes back when its attributes change
                  _key(p["product_type"], p["category"])))
    conn.commit()
    print(f"Approved {len(pending)} product type(s)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Weekly review of product type / Google category for the merchant feed")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("review", help="List new/changed proposals")
    a = sub.add_parser("approve", help="Approve proposals so the nightly feed sends them")
    a.add_argument("groupids", nargs="*")
    a.add_argument("--all", action="store_true", help="Approve everything pending review")
    a.add_argument("--type", dest="product_type", help="Override the product type for the given groupids")
    a.add_argument("--category", type=int, help="Override the Google category ID for the given groupids")
    args = parser.parse_args()

    if args.command == "approve" and not (args.groupids or args.all):
        parser.error("approve needs groupids or --all")

    conn = psycopg2.connect(**get_db_config())
    try:
        if args.command == "review":
            review(conn)
        else:
            approve(conn, args.groupids, args.product_type, args.category)
    finally:
        conn.close()
