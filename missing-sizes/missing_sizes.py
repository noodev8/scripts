#!/usr/bin/env python3
"""
Missing Sizes  —  Amazon size-coverage gap report.

Finds groupids that ARE on Amazon (at least one size live in `amzfeed`) but
are missing sizes that the brand normally carries. Existence in `skumap` is
NOT trusted as "the full range" — a test batch (e.g. only sizes 6/7 bought
in) only ever gets SKUs created for those sizes, so skumap itself under-states
the range for exactly the groupids we want to catch.

Instead, each brand's standard size sets are inferred as the exact sets of
sizes that recur (>=2 groupids share the identical set) across that brand's
groupids in skumap — established sets outvote one-off test batches, as long
as there's enough history. This is deliberately the exact recurring set, not
a generated min-to-max half-step range: brands routinely skip specific half
sizes (e.g. Strive carries 4,5,6,6.5,7,8 — no 4.5/5.5/7.5), so assuming a
contiguous run produces false positives on every groupid.

A brand can have more than one recurring set — e.g. Rieker sells both a
women's line (~4-7.5) and a men's line (~7.5-11) under the same brand, and
forcing one range onto both produces nonsense gaps on the other. So each
groupid is matched against whichever of its brand's recurring sets it
overlaps with most (by shared sizes), not a single brand-wide mode. Brands
with no recurring set at all (every groupid's size set is unique, or too few
groupids) are skipped and listed separately.

Only groupids with at least one actual Amazon sale (sales.channel='AMZ',
qty>0, ever) are reported — a groupid that's listed but has never sold isn't
worth filling out with more sizes.

    python missing_sizes.py
    python missing_sizes.py --brand Strive
    python missing_sizes.py --segment STRIVE-SEG

Output: one row per groupid with a gap — brand, groupid, colour, segment,
sizes currently listed on Amazon, sizes missing. Deliberately scoped to
"never listed" gaps only — does not check local warehouse stock and does not
flag sizes that are listed but currently out of FBA stock (that's a
different, restock-focused question).
"""

import os
import sys
import argparse
import csv
from collections import Counter, defaultdict
from decimal import Decimal

import psycopg2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from logging_utils import get_db_config

MIN_GROUPIDS_FOR_MODE = 3

QUERY = """
    SELECT ss.brand, ss.segment, ss.colour, sm.groupid, sm.code, sm.uksize,
           NULLIF(regexp_replace(sm.uksize, '[^0-9.]', '', 'g'), '')::numeric AS sizenum,
           (af.code IS NOT NULL) AS listed
    FROM skumap sm
    JOIN skusummary ss ON ss.groupid = sm.groupid
    LEFT JOIN amzfeed af ON af.code = sm.code
    WHERE sm.deleted = 0
      AND sm.uksize IS NOT NULL
      AND sm.uksize <> ''
"""

SOLD_QUERY = """
    SELECT DISTINCT groupid
    FROM sales
    WHERE channel = 'AMZ' AND qty > 0
"""


def fetch(brand, segment):
    sql = QUERY
    params = {}
    if brand:
        sql += " AND ss.brand = %(brand)s"
        params["brand"] = brand
    if segment:
        sql += " AND ss.segment = %(segment)s"
        params["segment"] = segment

    conn = psycopg2.connect(**get_db_config())
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.execute(SOLD_QUERY)
            sold_groupids = {r[0] for r in cur.fetchall()}
        return rows, sold_groupids
    finally:
        conn.close()


def analyse(rows, sold_groupids):
    """Returns (gaps, skipped_brands)."""
    groupids = defaultdict(lambda: {
        "brand": None, "segment": None, "colour": None,
        "sizes": set(), "listed_sizes": set(),
    })
    for brand, segment, colour, groupid, code, uksize, sizenum, listed in rows:
        if sizenum is None:
            continue
        g = groupids[groupid]
        g["brand"], g["segment"], g["colour"] = brand, segment, colour
        sizenum = Decimal(sizenum)
        g["sizes"].add(sizenum)
        if listed:
            g["listed_sizes"].add(sizenum)

    by_brand = defaultdict(list)
    for groupid, g in groupids.items():
        by_brand[g["brand"]].append((groupid, g))

    # Recurring size sets per brand: sets shared by >=2 groupids. A brand can
    # have several (e.g. a women's line and a men's line) — see module docstring.
    brand_clusters = {}
    skipped_brands = []
    for brand, glist in by_brand.items():
        if len(glist) < MIN_GROUPIDS_FOR_MODE:
            skipped_brands.append((brand, len(glist), "too few groupids"))
            continue
        set_counts = Counter(frozenset(g["sizes"]) for _, g in glist)
        clusters = [s for s, n in set_counts.items() if n >= 2]
        if not clusters:
            skipped_brands.append((brand, len(glist), "no recurring size set"))
            continue
        brand_clusters[brand] = clusters

    gaps = []
    for groupid, g in groupids.items():
        if not g["listed_sizes"]:
            continue  # not on Amazon at all — out of scope
        if groupid not in sold_groupids:
            continue  # listed but never sold on Amazon — not worth filling out
        clusters = brand_clusters.get(g["brand"])
        if not clusters:
            continue  # brand skipped for insufficient data
        # Best-matching recurring set for this groupid: most shared sizes;
        # tie-break on the larger candidate set.
        expected = sorted(clusters, key=lambda c: (len(c & g["sizes"]), len(c)), reverse=True)[0]
        missing = sorted(expected - g["listed_sizes"])
        if missing:
            gaps.append({
                "brand": g["brand"], "segment": g["segment"], "colour": g["colour"],
                "groupid": groupid,
                "listed": sorted(g["listed_sizes"]),
                "missing": missing,
                "expected": expected,
            })

    return gaps, skipped_brands


def fmt_sizes(sizes):
    out = []
    for s in sizes:
        out.append(str(int(s)) if s == s.to_integral_value() else str(s))
    return ",".join(out)


CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "missing_sizes.csv")


def write_csv(gaps, path=CSV_PATH):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["groupid", "missing_sizes"])
        for r in sorted(gaps, key=lambda r: (r["brand"], sorted(r["expected"]), -len(r["missing"]), r["groupid"])):
            writer.writerow([r["groupid"], fmt_sizes(r["missing"])])


def render(gaps, skipped_brands, brand_filter, segment_filter):
    print()
    label = brand_filter or segment_filter or "all brands"
    print(f"Amazon size gaps  |  {label}")
    print("=" * 78)

    if skipped_brands:
        by_reason = defaultdict(list)
        for b, n, reason in skipped_brands:
            by_reason[reason].append(f"{b} ({n} groupid{'s' if n != 1 else ''})")
        for reason, names in by_reason.items():
            print(f"Skipped ({reason}): {', '.join(sorted(names))}")
        print()

    if not gaps:
        print("  (no size gaps found)")
        print()
        return

    gaps.sort(key=lambda r: (r["brand"], sorted(r["expected"]), -len(r["missing"]), r["groupid"]))

    last_key = None
    for r in gaps:
        key = (r["brand"], r["expected"])
        if key != last_key:
            std = sorted(r["expected"])
            print(f"\n{r['brand']}  (standard sizes {fmt_sizes(std)} UK)")
            print("-" * 78)
            last_key = key
        print(f"  {r['groupid']:<20} {str(r['colour'] or ''):<10} {str(r['segment'] or ''):<16} "
              f"listed: {fmt_sizes(r['listed']):<16} missing: {fmt_sizes(r['missing'])}")
    print()


def main():
    ap = argparse.ArgumentParser(description="Find Amazon-listed groupids missing sizes vs the brand's standard range.")
    ap.add_argument("--brand", help="filter to one brand (skusummary.brand)")
    ap.add_argument("--segment", help="filter to one segment (skusummary.segment)")
    args = ap.parse_args()

    rows, sold_groupids = fetch(args.brand, args.segment)
    gaps, skipped_brands = analyse(rows, sold_groupids)
    render(gaps, skipped_brands, args.brand, args.segment)
    write_csv(gaps)
    print(f"CSV written: {CSV_PATH}")


if __name__ == "__main__":
    main()
